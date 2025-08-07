"""
YouTube 학습 시스템 API 엔드포인트
YouTube 영상에서 사주 지식 학습 및 활용
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from app.core.dependencies import get_db, get_current_admin_user, get_current_user
from app.core.response import SuccessResponse, create_success_response
from app.models.user import User
from app.services.youtube_service import YouTubeService

router = APIRouter()

# Request Models
class VideoLearningRequest(BaseModel):
    """단일 영상 학습 요청"""
    video_id: str = Field(..., description="YouTube 영상 ID")
    
class BatchVideoLearningRequest(BaseModel):
    """일괄 영상 학습 요청"""
    video_ids: List[str] = Field(..., description="YouTube 영상 ID 목록")
    
class KnowledgeSearchRequest(BaseModel):
    """지식 검색 요청"""
    query: str = Field(..., description="검색 쿼리")
    limit: int = Field(10, ge=1, le=50, description="검색 결과 수")

# Response Models
class VideoLearningResponse(BaseModel):
    """영상 학습 응답"""
    success: bool
    video_id: str
    learned_sentences: int
    total_sentences: int
    video_info: Dict[str, Any] = {}
    error: str = None

class KnowledgeSummaryResponse(BaseModel):
    """지식 요약 응답"""
    total_knowledge_entries: int
    total_videos_processed: int
    sentence_type_distribution: Dict[str, int]
    average_confidence: float
    database_path: str

class KnowledgeSearchResponse(BaseModel):
    """지식 검색 응답"""
    video_id: str
    video_title: str
    content: str
    saju_terms: Dict[str, List[str]]
    sentence_type: str
    confidence: float
    created_at: str

@router.post(
    "/learn/single",
    response_model=SuccessResponse[VideoLearningResponse],
    summary="단일 영상 학습",
    description="YouTube 영상 하나에서 사주 관련 지식을 학습합니다."
)
async def learn_from_single_video(
    request: VideoLearningRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> SuccessResponse[VideoLearningResponse]:
    """단일 영상에서 사주 지식 학습"""
    
    youtube_service = YouTubeService(db)
    
    try:
        result = await youtube_service.learn_from_video(request.video_id)
        
        response = VideoLearningResponse(**result)
        
        return create_success_response(
            data=response,
            message=f"영상 {request.video_id} 학습을 완료했습니다."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"영상 학습 중 오류가 발생했습니다: {str(e)}"
        )

@router.post(
    "/learn/batch",
    response_model=SuccessResponse[Dict[str, Any]],
    summary="일괄 영상 학습",
    description="여러 YouTube 영상에서 사주 관련 지식을 일괄 학습합니다."
)
async def learn_from_multiple_videos(
    request: BatchVideoLearningRequest,
    background_tasks: BackgroundTasks,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> SuccessResponse[Dict[str, Any]]:
    """여러 영상에서 일괄 학습 (백그라운드 처리)"""
    
    if len(request.video_ids) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="한 번에 학습할 수 있는 최대 영상 수는 20개입니다."
        )
    
    # 백그라운드 태스크로 일괄 학습 실행
    async def batch_learning_task():
        youtube_service = YouTubeService(db)
        await youtube_service.batch_learn_from_videos(request.video_ids)
    
    background_tasks.add_task(batch_learning_task)
    
    return create_success_response(
        data={
            "task_started": True,
            "video_count": len(request.video_ids),
            "video_ids": request.video_ids
        },
        message=f"{len(request.video_ids)}개 영상의 일괄 학습이 백그라운드에서 시작되었습니다."
    )

@router.get(
    "/knowledge/summary",
    response_model=SuccessResponse[KnowledgeSummaryResponse],
    summary="학습된 지식 요약",
    description="현재까지 학습된 사주 지식의 전체 요약을 제공합니다."
)
async def get_knowledge_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse[KnowledgeSummaryResponse]:
    """학습된 지식 요약 조회"""
    
    youtube_service = YouTubeService(db)
    
    try:
        summary = await youtube_service.get_knowledge_summary()
        
        response = KnowledgeSummaryResponse(**summary)
        
        return create_success_response(
            data=response,
            message="지식 요약을 성공적으로 조회했습니다."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"지식 요약 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.post(
    "/knowledge/search",
    response_model=SuccessResponse[List[KnowledgeSearchResponse]],
    summary="지식 검색",
    description="학습된 사주 지식에서 특정 내용을 검색합니다."
)
async def search_knowledge(
    request: KnowledgeSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse[List[KnowledgeSearchResponse]]:
    """학습된 지식 검색"""
    
    youtube_service = YouTubeService(db)
    
    try:
        results = await youtube_service.search_knowledge(request.query, request.limit)
        
        response = [KnowledgeSearchResponse(**result) for result in results]
        
        return create_success_response(
            data=response,
            message=f"'{request.query}' 검색을 완료했습니다."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"지식 검색 중 오류가 발생했습니다: {str(e)}"
        )

@router.get(
    "/knowledge/personalized",
    response_model=SuccessResponse[List[KnowledgeSearchResponse]],
    summary="개인 맞춤형 지식 조회",
    description="사용자의 사주 정보에 맞춤화된 지식을 제공합니다."
)
async def get_personalized_knowledge(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse[List[KnowledgeSearchResponse]]:
    """개인 맞춤형 사주 지식 조회"""
    
    # 사용자의 사주 프로필 확인
    from app.services.saju_service import SajuService
    saju_service = SajuService(db)
    saju_profile = await saju_service.get_saju_profile(current_user.id)
    
    if not saju_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사주 프로필이 없습니다. 먼저 사주 분석을 진행해주세요."
        )
    
    # 생년월일 정보 추출
    birth_info = saju_profile.birth_info
    
    youtube_service = YouTubeService(db)
    
    try:
        results = await youtube_service.get_personalized_knowledge(birth_info)
        
        response = [KnowledgeSearchResponse(**result) for result in results]
        
        return create_success_response(
            data=response,
            message="개인 맞춤형 사주 지식을 성공적으로 조회했습니다."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"개인 맞춤형 지식 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get(
    "/system/status",
    response_model=SuccessResponse[Dict[str, Any]],
    summary="YouTube 학습 시스템 상태",
    description="YouTube 학습 시스템의 현재 상태를 확인합니다."
)
async def get_system_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse[Dict[str, Any]]:
    """YouTube 학습 시스템 상태 확인"""
    
    try:
        # 필요한 라이브러리 설치 상태 확인
        system_status = {
            "youtube_transcript_api": True,  # 기본 설치됨
            "yt_dlp": True,  # 기본 설치됨
            "sentence_transformers": False,
            "whisper": False,
            "moviepy": False
        }
        
        # 선택적 라이브러리 확인
        try:
            import sentence_transformers
            system_status["sentence_transformers"] = True
        except ImportError:
            pass
            
        try:
            import whisper
            system_status["whisper"] = True
        except ImportError:
            pass
            
        try:
            import moviepy
            system_status["moviepy"] = True
        except ImportError:
            pass
        
        # 지식 데이터베이스 상태
        youtube_service = YouTubeService(db)
        knowledge_summary = await youtube_service.get_knowledge_summary()
        
        status_data = {
            "library_status": system_status,
            "knowledge_database": knowledge_summary,
            "features_available": {
                "transcript_learning": True,
                "audio_processing": system_status["whisper"] and system_status["moviepy"],
                "semantic_search": system_status["sentence_transformers"],
                "advanced_nlp": system_status["sentence_transformers"]
            }
        }
        
        return create_success_response(
            data=status_data,
            message="YouTube 학습 시스템 상태를 성공적으로 조회했습니다."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"시스템 상태 확인 중 오류가 발생했습니다: {str(e)}"
        )