"""
사주 유튜브 영상 관련 CRUD 함수들
"""

from sqlalchemy.orm import Session
from models import SajuVideo, SajuVideoInteraction
from typing import List, Optional, Dict
import datetime

def create_saju_video(db: Session, video_data: Dict) -> SajuVideo:
    """새로운 사주 영상 정보 저장"""
    
    # 이미 존재하는 영상인지 확인
    existing_video = db.query(SajuVideo).filter(
        SajuVideo.video_id == video_data.get('video_id')
    ).first()
    
    if existing_video:
        # 기존 영상 정보 업데이트
        for key, value in video_data.items():
            if hasattr(existing_video, key):
                setattr(existing_video, key, value)
        existing_video.crawled_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(existing_video)
        return existing_video
    
    # 새 영상 생성
    db_video = SajuVideo(
        video_id=video_data.get('video_id'),
        title=video_data.get('title', ''),
        description=video_data.get('description', ''),
        channel_title=video_data.get('channel_title', ''),
        published_at=video_data.get('published_at', ''),
        thumbnail_url=video_data.get('thumbnail_url', ''),
        url=video_data.get('url', ''),
        keyword=video_data.get('keyword', ''),
        relevance_score=video_data.get('relevance_score', 0),
        view_count=video_data.get('view_count', 0),
        like_count=video_data.get('like_count', 0),
        comment_count=video_data.get('comment_count', 0),
        duration=video_data.get('duration', ''),
        saju_terms=video_data.get('saju_terms', []),
        fortune_keywords=video_data.get('fortune_keywords', []),
        content_type=video_data.get('content_type', '일반'),
        target_audience=video_data.get('target_audience', '전체')
    )
    
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

def get_saju_videos(
    db: Session, 
    skip: int = 0, 
    limit: int = 20,
    content_type: Optional[str] = None,
    target_audience: Optional[str] = None,
    keyword: Optional[str] = None
) -> List[SajuVideo]:
    """사주 영상 목록 조회"""
    
    query = db.query(SajuVideo).filter(SajuVideo.is_active == True)
    
    if content_type:
        query = query.filter(SajuVideo.content_type == content_type)
    
    if target_audience:
        query = query.filter(SajuVideo.target_audience == target_audience)
    
    if keyword:
        query = query.filter(
            SajuVideo.title.contains(keyword) | 
            SajuVideo.description.contains(keyword)
        )
    
    return query.order_by(SajuVideo.relevance_score.desc()).offset(skip).limit(limit).all()

def get_saju_video_by_id(db: Session, video_id: str) -> Optional[SajuVideo]:
    """특정 유튜브 영상 조회"""
    return db.query(SajuVideo).filter(SajuVideo.video_id == video_id).first()

def get_popular_saju_videos(db: Session, limit: int = 10) -> List[SajuVideo]:
    """인기 사주 영상 조회 (조회수 기준)"""
    return db.query(SajuVideo)\
        .filter(SajuVideo.is_active == True)\
        .order_by(SajuVideo.view_count.desc())\
        .limit(limit)\
        .all()

def get_recent_saju_videos(db: Session, limit: int = 10) -> List[SajuVideo]:
    """최신 사주 영상 조회"""
    return db.query(SajuVideo)\
        .filter(SajuVideo.is_active == True)\
        .order_by(SajuVideo.crawled_at.desc())\
        .limit(limit)\
        .all()

def get_videos_by_content_type(db: Session, content_type: str, limit: int = 10) -> List[SajuVideo]:
    """컨텐츠 타입별 영상 조회"""
    return db.query(SajuVideo)\
        .filter(SajuVideo.content_type == content_type, SajuVideo.is_active == True)\
        .order_by(SajuVideo.relevance_score.desc())\
        .limit(limit)\
        .all()

def search_saju_videos(db: Session, search_term: str, limit: int = 20) -> List[SajuVideo]:
    """사주 영상 검색"""
    return db.query(SajuVideo)\
        .filter(
            SajuVideo.is_active == True,
            (SajuVideo.title.contains(search_term) | 
             SajuVideo.description.contains(search_term) |
             SajuVideo.channel_title.contains(search_term))
        )\
        .order_by(SajuVideo.relevance_score.desc())\
        .limit(limit)\
        .all()

def create_video_interaction(
    db: Session, 
    user_id: int, 
    video_id: int, 
    interaction_type: str
) -> SajuVideoInteraction:
    """사용자 영상 상호작용 기록"""
    
    interaction = SajuVideoInteraction(
        user_id=user_id,
        video_id=video_id,
        interaction_type=interaction_type
    )
    
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction

def get_user_video_interactions(
    db: Session, 
    user_id: int, 
    interaction_type: Optional[str] = None
) -> List[SajuVideoInteraction]:
    """사용자의 영상 상호작용 기록 조회"""
    
    query = db.query(SajuVideoInteraction).filter(
        SajuVideoInteraction.user_id == user_id
    )
    
    if interaction_type:
        query = query.filter(SajuVideoInteraction.interaction_type == interaction_type)
    
    return query.order_by(SajuVideoInteraction.created_at.desc()).all()

def get_video_statistics(db: Session) -> Dict:
    """사주 영상 통계 조회"""
    
    total_videos = db.query(SajuVideo).filter(SajuVideo.is_active == True).count()
    
    # 컨텐츠 타입별 통계
    content_type_stats = db.query(
        SajuVideo.content_type, 
        db.func.count(SajuVideo.id).label('count')
    ).filter(SajuVideo.is_active == True).group_by(SajuVideo.content_type).all()
    
    # 대상 청중별 통계
    audience_stats = db.query(
        SajuVideo.target_audience,
        db.func.count(SajuVideo.id).label('count')
    ).filter(SajuVideo.is_active == True).group_by(SajuVideo.target_audience).all()
    
    # 채널별 통계 (상위 10개)
    channel_stats = db.query(
        SajuVideo.channel_title,
        db.func.count(SajuVideo.id).label('count')
    ).filter(SajuVideo.is_active == True)\
     .group_by(SajuVideo.channel_title)\
     .order_by(db.func.count(SajuVideo.id).desc())\
     .limit(10).all()
    
    return {
        'total_videos': total_videos,
        'content_types': {stat.content_type: stat.count for stat in content_type_stats},
        'target_audiences': {stat.target_audience: stat.count for stat in audience_stats},
        'top_channels': [(stat.channel_title, stat.count) for stat in channel_stats]
    }

def update_video_stats(db: Session, video_id: str, stats_data: Dict) -> Optional[SajuVideo]:
    """영상 통계 업데이트 (조회수, 좋아요 등)"""
    
    video = db.query(SajuVideo).filter(SajuVideo.video_id == video_id).first()
    if not video:
        return None
    
    if 'view_count' in stats_data:
        video.view_count = stats_data['view_count']
    if 'like_count' in stats_data:
        video.like_count = stats_data['like_count']
    if 'comment_count' in stats_data:
        video.comment_count = stats_data['comment_count']
    
    db.commit()
    db.refresh(video)
    return video

def delete_saju_video(db: Session, video_id: str) -> bool:
    """사주 영상 삭제 (소프트 삭제)"""
    
    video = db.query(SajuVideo).filter(SajuVideo.video_id == video_id).first()
    if not video:
        return False
    
    video.is_active = False
    db.commit()
    return True

def bulk_create_saju_videos(db: Session, videos_data: List[Dict]) -> List[SajuVideo]:
    """여러 사주 영상 일괄 저장"""
    
    created_videos = []
    for video_data in videos_data:
        try:
            video = create_saju_video(db, video_data)
            created_videos.append(video)
        except Exception as e:
            print(f"영상 저장 실패 ({video_data.get('video_id')}): {str(e)}")
            continue
    
    return created_videos