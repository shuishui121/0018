"""剧种路由"""
from typing import List, Dict, Optional, Set
from collections import deque

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/genres", tags=["剧种"])

MAX_GENERATIONS = 5


def _inheritor_to_list(ih: models.Inheritor) -> schemas.InheritorListItem:
    return schemas.InheritorListItem(
        id=ih.id,
        name=ih.name,
        pinyin_initial=ih.pinyin_initial,
        gender=ih.gender,
        birth_date=ih.birth_date,
        age_group=ih.age_group,
        genre_id=ih.genre_id,
        genre_name=ih.genre.name if ih.genre else None,
        role_type=ih.role_type,
        region=ih.region,
        avatar=ih.avatar,
        master_id=ih.master_id,
        master_name=ih.master.name if ih.master else None,
        bio=ih.bio,
    )


RELATION_LABELS_GENEALOGY = {
    "master_apprentice": "师徒传承",
}


@router.get("", response_model=List[schemas.Genre])
def list_genres(db: Session = Depends(get_db)):
    genres = db.query(models.Genre).order_by(models.Genre.id.asc()).all()
    return genres


@router.get("/{genre_id}", response_model=schemas.GenreDetail)
def get_genre(genre_id: int, db: Session = Depends(get_db)):
    genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if not genre:
        raise HTTPException(status_code=404, detail="剧种不存在")
    inheritors = [_inheritor_to_list(ih) for ih in genre.inheritors]
    return schemas.GenreDetail(
        id=genre.id,
        name=genre.name,
        pinyin=genre.pinyin,
        history=genre.history,
        art_features=genre.art_features,
        classic_plays=genre.classic_plays,
        main_schools=genre.main_schools,
        distribution_areas=genre.distribution_areas,
        cover_image=genre.cover_image,
        inheritors=inheritors,
        troupes=genre.troupes,
    )


@router.get("/{genre_id}/genealogy", response_model=schemas.GenealogyResponse)
def get_genre_genealogy(
    genre_id: int,
    max_generations: int = Query(MAX_GENERATIONS, ge=1, le=10, description="最多追溯代数"),
    keyword: Optional[str] = Query(None, description="姓名关键词筛选"),
    region: Optional[str] = Query(None, description="地区过滤"),
    db: Session = Depends(get_db),
):
    """获取剧种的传承人谱系树状结构，支持最多五代人层级查询"""
    genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if not genre:
        raise HTTPException(status_code=404, detail="剧种不存在")

    # 获取该剧种所有传承人
    all_inheritors = (
        db.query(models.Inheritor)
          .filter(models.Inheritor.genre_id == genre_id)
          .all()
    )
    if not all_inheritors:
        return schemas.GenealogyResponse(
            genre=schemas.Genre.model_validate(genre),
            nodes=[],
            edges=[],
            max_generation=0,
        )

    ih_by_id: Dict[int, models.Inheritor] = {ih.id: ih for ih in all_inheritors}

    # 1. 找出所有第一代宗师（没有师傅，或者师傅不在本剧种内的）
    roots: List[models.Inheritor] = []
    for ih in all_inheritors:
        if not ih.master_id or ih.master_id not in ih_by_id:
            roots.append(ih)

    # 如果全部是闭环或找不到根，用所有无master_id的或直接取按出生年最早的几个
    if not roots:
        roots = [ih for ih in all_inheritors if not ih.master_id]
    if not roots:
        sorted_ihs = sorted(all_inheritors, key=lambda x: (x.birth_date or "9999-12-31"))
        roots = sorted_ihs[:max(1, len(sorted_ihs) // 5)]

    # 2. 用 BFS 从根节点构建层级，限制最大代数
    generation_map: Dict[int, int] = {}  # inheritor_id -> generation (1 起)
    edges_map: Dict[tuple, str] = {}  # (source, target) -> relation_label
    visited: Set[int] = set()
    queue = deque()

    for root in roots:
        generation_map[root.id] = 1
        visited.add(root.id)
        queue.append((root.id, 1))

    while queue:
        current_id, gen = queue.popleft()
        if gen >= max_generations:
            continue

        # 找到所有以 current_id 为师傅的徒弟
        apprentices = [
            ih for ih in all_inheritors
            if ih.master_id == current_id and ih.id not in visited
        ]
        for app in apprentices:
            generation_map[app.id] = gen + 1
            edges_map[(current_id, app.id)] = "师徒传承"
            visited.add(app.id)
            queue.append((app.id, gen + 1))

    # 处理剩余未访问的节点（可能形成独立树），把它们作为新根放到下一代
    leftover = [ih for ih in all_inheritors if ih.id not in visited]
    if leftover:
        next_gen = max(generation_map.values()) + 1 if generation_map else 1
        for ih in leftover:
            if next_gen <= max_generations:
                generation_map[ih.id] = next_gen
                visited.add(ih.id)
                if ih.master_id and ih.master_id in ih_by_id:
                    edges_map[(ih.master_id, ih.id)] = "师徒传承"

    # 3. 从 inheritor_relations 表增加额外连线（同门、亲属等），但不作为层级计算
    extra_rels = (
        db.query(models.InheritorRelation)
          .filter(
              models.InheritorRelation.from_inheritor_id.in_(list(ih_by_id.keys())),
              models.InheritorRelation.to_inheritor_id.in_(list(ih_by_id.keys())),
          )
          .all()
    )

    # 4. 构建节点列表
    nodes: List[schemas.GenealogyNode] = []
    edges: List[schemas.GenealogyEdge] = []
    actual_max_gen = 0

    # 关键词和地区过滤
    def match_filter(ih: models.Inheritor) -> bool:
        if keyword and keyword not in (ih.name or ""):
            return False
        if region and region not in (ih.region or ""):
            return False
        return True

    # 为了图谱的完整性，过滤节点后保留相连边
    matched_ids: Set[int] = set()

    for ih_id, gen in generation_map.items():
        ih = ih_by_id[ih_id]
        if not ih:
            continue
        node = schemas.GenealogyNode(
            id=ih.id,
            name=ih.name,
            role_type=ih.role_type,
            avatar=ih.avatar,
            region=ih.region,
            genre_id=ih.genre_id,
            master_id=ih.master_id,
            generation=gen,
            children=[],
        )
        nodes.append(node)
        actual_max_gen = max(actual_max_gen, gen)
        if match_filter(ih):
            matched_ids.add(ih.id)

    # 构建师徒连线
    for (src, tgt), label in edges_map.items():
        edges.append(schemas.GenealogyEdge(
            source=src,
            target=tgt,
            relation_type="master_apprentice",
            relation_label=label,
        ))

    # 构建额外关系连线
    relation_label_map = {
        "master": "师徒",
        "apprentice": "师徒",
        "sibling": "兄弟姐妹",
        "spouse": "配偶",
        "parent": "父子/女",
        "child": "母子/女",
        "cousin": "表亲",
        "colleague": "同事",
        "friend": "友人",
        "senior_fellow": "同门",
        "junior_fellow": "同门",
    }
    for r in extra_rels:
        label = relation_label_map.get(r.relation_type, r.relation_type)
        # 避免重复边
        key1 = (r.from_inheritor_id, r.to_inheritor_id)
        key2 = (r.to_inheritor_id, r.from_inheritor_id)
        exists = any(
            (e.source == key1[0] and e.target == key1[1]) or
            (e.source == key2[0] and e.target == key2[1])
            for e in edges
        )
        if not exists:
            edges.append(schemas.GenealogyEdge(
                source=r.from_inheritor_id,
                target=r.to_inheritor_id,
                relation_type=r.relation_type,
                relation_label=label,
            ))

    # 5. 构建子节点关系（用于树图渲染的 children 字段）
    node_by_id = {n.id: n for n in nodes}
    for (src, tgt), _label in edges_map.items():
        if src in node_by_id and tgt in node_by_id:
            node_by_id[src].children.append(node_by_id[tgt])

    # 如果有关键词或地区过滤，确保被匹配的节点的上下师父徒关系也被纳入
    if keyword or region:
        highlighted_ids = set(matched_ids)
        # 向上追溯师傅
        for nid in list(matched_ids):
            cur = nid
            for _ in range(max_generations):
                node = node_by_id.get(cur)
                if not node or not node.master_id:
                    break
                highlighted_ids.add(node.master_id)
                cur = node.master_id
        # 向下找徒弟
        def collect_down(nid: int):
            node = node_by_id.get(nid)
            if not node:
                return
            for c in node.children:
                highlighted_ids.add(c.id)
                collect_down(c.id)
        for nid in list(matched_ids):
            collect_down(nid)

        nodes = [n for n in nodes if n.id in highlighted_ids]
        kept_node_ids = {n.id for n in nodes}
        edges = [e for e in edges if e.source in kept_node_ids and e.target in kept_node_ids]

    return schemas.GenealogyResponse(
        genre=schemas.Genre.model_validate(genre),
        nodes=nodes,
        edges=edges,
        max_generation=actual_max_gen,
    )
