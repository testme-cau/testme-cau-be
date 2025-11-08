# 테스트 리팩토링 가이드

## 현재 상태

**테스트 통과율**: 51개 중 47개 통과 (92%)

리팩토링 후 백엔드 아키텍처가 Repository Pattern과 Service Layer를 도입하면서 일부 테스트가 업데이트되어야 합니다.

## 실패한 테스트 목록

### 1. PDF Routes 테스트 (3개)

- `tests/test_pdf_routes.py::test_upload_pdf_success`
- `tests/test_pdf_routes.py::test_get_pdf_download_url`
- `tests/test_pdf_routes.py::test_delete_pdf`

**실패 원인**: 
- 리팩토링 전: `app.routes.pdf`에서 직접 `FirebaseStorageService` import
- 리팩토링 후: `PDFService`를 통한 dependency injection
- 기존 mock 경로가 더 이상 유효하지 않음

### 2. Subject Routes 테스트 (1개)

- `tests/test_subject_routes.py::test_update_subject_success`

**실패 원인**:
- 리팩토링 전: 라우트에서 직접 Firestore 접근
- 리팩토링 후: `SubjectService`를 통한 비즈니스 로직 처리
- Mock 설정이 새로운 서비스 계층 구조를 반영하지 못함

## 해결 방안

### 방안 1: Service Layer Mock (권장) ⭐

**장점**: 
- 빠른 실행 속도
- 외부 의존성 없음
- 단위 테스트 원칙 준수

**단점**:
- Mock 설정이 복잡할 수 있음
- 서비스 계층 변경 시 테스트도 함께 수정 필요

**구현 예시**:

```python
# test_pdf_routes.py
from unittest.mock import Mock, patch
from datetime import datetime
from app.models.domain import Subject, PDF

@patch('app.dependencies.service.get_pdf_service')
@patch('app.dependencies.service.get_subject_service')
def test_upload_pdf_success(
    mock_get_subject_service,
    mock_get_pdf_service,
    client,
    auth_override
):
    """Test PDF upload through service layer"""
    
    # 1. Mock SubjectService
    mock_subject_service = Mock()
    mock_subject = Subject(
        subject_id="test_subject_123",
        user_id="test_user_123",
        name="Test Subject",
        created_at=datetime.utcnow()
    )
    mock_subject_service.get_subject.return_value = mock_subject
    mock_get_subject_service.return_value = mock_subject_service
    
    # 2. Mock PDFService
    mock_pdf_service = Mock()
    mock_pdf_service.upload_pdf.return_value = {
        'file_id': 'test_pdf_123',
        'original_filename': 'test.pdf',
        'file_url': '/api/subjects/test_subject_123/pdfs/test_pdf_123/download',
        'size': 1024,
        'uploaded_at': datetime.utcnow()
    }
    mock_get_pdf_service.return_value = mock_pdf_service
    
    # 3. Make request
    from io import BytesIO
    pdf_content = b'%PDF-1.4\n%Mock PDF content\n%%EOF'
    files = {'file': ('test.pdf', BytesIO(pdf_content), 'application/pdf')}
    response = client.post(
        "/api/subjects/test_subject_123/pdfs/upload",
        files=files
    )
    
    # 4. Assertions
    assert response.status_code == 201
    data = response.json()
    assert data['success'] is True
    assert data['file_id'] == 'test_pdf_123'
    assert data['original_filename'] == 'test.pdf'
    
    # 5. Verify service calls
    mock_pdf_service.upload_pdf.assert_called_once()
```

**추가 구현 필요**:

```python
@patch('app.dependencies.service.get_pdf_service')
@patch('app.dependencies.service.get_subject_service')
def test_get_pdf_download_url(
    mock_get_subject_service,
    mock_get_pdf_service,
    client,
    auth_override
):
    """Test PDF download URL generation"""
    mock_pdf_service = Mock()
    mock_pdf_service.get_download_url.return_value = {
        'download_url': 'https://storage.googleapis.com/...',
        'filename': 'test.pdf'
    }
    mock_get_pdf_service.return_value = mock_pdf_service
    
    # ... implementation
```

```python
@patch('app.dependencies.service.get_pdf_service')
def test_delete_pdf(
    mock_get_pdf_service,
    client,
    auth_override
):
    """Test PDF deletion"""
    mock_pdf_service = Mock()
    mock_pdf_service.delete_pdf.return_value = None
    mock_get_pdf_service.return_value = mock_pdf_service
    
    response = client.delete("/api/subjects/test_subject_123/pdfs/test_pdf_123")
    assert response.status_code == 200
```

```python
@patch('app.dependencies.service.get_subject_service')
def test_update_subject_success(
    mock_get_subject_service,
    client,
    auth_override
):
    """Test subject update through service layer"""
    mock_subject_service = Mock()
    
    updated_subject = Subject(
        subject_id="test_subject_123",
        user_id="test_user_123",
        name="Updated Database",
        description="Updated description",
        group_id=None,
        color="#FF5733",
        created_at=datetime.utcnow()
    )
    
    mock_subject_service.update_subject.return_value = updated_subject
    mock_get_subject_service.return_value = mock_subject_service
    
    response = client.put(
        "/api/subjects/test_subject_123",
        json={"name": "Updated Database"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert data['subject']['name'] == 'Updated Database'
```

### 방안 2: Firebase Emulator 통합 테스트

**장점**:
- 실제 Firebase 동작 테스트
- Mock 설정 불필요
- 더 높은 신뢰도

**단점**:
- 느린 실행 속도
- Firebase Emulator 설치 필요
- CI/CD 파이프라인 복잡도 증가

**설정 방법**:

1. **Firebase Emulator 설치**:
```bash
npm install -g firebase-tools
```

2. **`firebase.json` 생성**:
```json
{
  "emulators": {
    "firestore": {
      "port": 8080
    },
    "storage": {
      "port": 9199
    },
    "auth": {
      "port": 9099
    }
  }
}
```

3. **`tests/conftest.py` 수정**:
```python
import pytest
import os

@pytest.fixture(scope="session", autouse=True)
def setup_firebase_emulator():
    """Setup Firebase emulator environment variables"""
    os.environ['FIRESTORE_EMULATOR_HOST'] = 'localhost:8080'
    os.environ['FIREBASE_STORAGE_EMULATOR_HOST'] = 'localhost:9199'
    os.environ['FIREBASE_AUTH_EMULATOR_HOST'] = 'localhost:9099'
    yield
```

4. **테스트 실행**:
```bash
# Terminal 1: Start emulator
firebase emulators:start

# Terminal 2: Run tests
pytest tests/
```

### 방안 3: 임시 스킵 (빠른 배포용)

**테스트에 skip 마커 추가**:

```python
import pytest

@pytest.mark.skip(reason="Requires refactoring for new service layer architecture")
def test_upload_pdf_success(...):
    pass

@pytest.mark.skip(reason="Requires refactoring for new service layer architecture")
def test_get_pdf_download_url(...):
    pass

@pytest.mark.skip(reason="Requires refactoring for new service layer architecture")
def test_delete_pdf(...):
    pass

@pytest.mark.skip(reason="Requires refactoring for new service layer architecture")
def test_update_subject_success(...):
    pass
```

**주의**: 이 방법은 **임시 조치**일 뿐이며, 실제 테스트 커버리지가 감소합니다.

## 권장 작업 순서

### 즉시 (1시간)
1. ✅ 도메인 모델 테스트 수정 완료
2. ✅ Subject routes 기본 테스트 통과 (create, list, get, delete)
3. ⏳ **다음**: 방안 1에 따라 실패한 4개 테스트 재작성

### 단기 (2-3시간)
1. PDF routes 3개 테스트 재작성
2. Subject update 테스트 재작성
3. 새로운 Repository & Service 계층 유닛 테스트 추가

### 중기 (1일)
1. Firebase Emulator 기반 통합 테스트 구축
2. CI/CD 파이프라인에 Emulator 통합
3. 테스트 커버리지 90% 이상 달성

## 추가 개선 사항

### 1. Repository 계층 유닛 테스트 추가

**`tests/test_repositories.py`** 생성 (신규):

```python
"""Repository layer unit tests"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.repositories.subject import SubjectRepository
from app.models.domain import Subject

@patch('firebase_admin.firestore.client')
def test_subject_repository_create(mock_firestore):
    """Test SubjectRepository.create"""
    repo = SubjectRepository()
    
    # Mock Firestore
    mock_db = Mock()
    mock_collection_ref = Mock()
    mock_doc_ref = Mock()
    
    mock_db.collection.return_value.document.return_value.collection.return_value = mock_collection_ref
    mock_collection_ref.document.return_value = mock_doc_ref
    mock_doc_ref.get.return_value.to_dict.return_value = {
        'subject_id': 'test_123',
        'user_id': 'user_123',
        'name': 'Test Subject',
        'created_at': datetime.utcnow()
    }
    mock_firestore.return_value = mock_db
    
    # Test create
    result = repo.create({
        'subject_id': '',
        'user_id': 'user_123',
        'name': 'Test Subject'
    }, user_id='user_123')
    
    assert result is not None
    mock_doc_ref.set.assert_called_once()
```

### 2. Service 계층 유닛 테스트 추가

**`tests/test_services.py`** 생성 (신규):

```python
"""Service layer unit tests"""
import pytest
from unittest.mock import Mock
from app.services.subject_service import SubjectService
from app.models.requests import SubjectCreateRequest, SubjectUpdateRequest
from app.models.domain import Subject

def test_subject_service_create():
    """Test SubjectService.create_subject"""
    # Mock repository
    mock_repo = Mock()
    mock_repo.create.return_value = {
        'subject_id': 'test_123',
        'user_id': 'user_123',
        'name': 'Test Subject',
        'description': None,
        'group_id': None,
        'color': None,
        'created_at': datetime.utcnow()
    }
    
    # Create service with mock
    service = SubjectService(subject_repo=mock_repo)
    
    # Test create
    request = SubjectCreateRequest(name='Test Subject')
    result = service.create_subject('user_123', request)
    
    assert isinstance(result, Subject)
    assert result.name == 'Test Subject'
    mock_repo.create.assert_called_once()

def test_subject_service_update():
    """Test SubjectService.update_subject"""
    mock_repo = Mock()
    
    # Mock get_by_id_with_ownership
    mock_repo.get_by_id_with_ownership.return_value = {
        'subject_id': 'test_123',
        'user_id': 'user_123',
        'name': 'Old Name'
    }
    
    # Mock update
    mock_repo.update.return_value = {
        'subject_id': 'test_123',
        'user_id': 'user_123',
        'name': 'New Name',
        'created_at': datetime.utcnow()
    }
    
    service = SubjectService(subject_repo=mock_repo)
    request = SubjectUpdateRequest(name='New Name')
    result = service.update_subject('user_123', 'test_123', request)
    
    assert result.name == 'New Name'
    mock_repo.update.assert_called_once()
```

### 3. 프론트엔드 Custom Hooks 테스트

**`web-frontend/src/hooks/__tests__/useSubject.test.ts`** 생성 (신규):

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { useSubject } from '../useSubject';
import { getSubject } from '@/lib/api/subjects';

jest.mock('@/lib/api/subjects');

describe('useSubject', () => {
  it('should fetch subject on mount', async () => {
    const mockSubject = {
      subject_id: 'test_123',
      name: 'Test Subject',
      user_id: 'user_123',
      created_at: new Date().toISOString()
    };
    
    (getSubject as jest.Mock).mockResolvedValue(mockSubject);
    
    const { result } = renderHook(() => useSubject('test_123'));
    
    expect(result.current.loading).toBe(true);
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    expect(result.current.subject).toEqual(mockSubject);
  });
});
```

## 예상 시간

- **방안 1 구현**: 2-3시간
- **방안 2 구현**: 6-8시간 (emulator 설정 포함)
- **방안 3 구현**: 5분

## 결론

**즉시 권장**: 방안 1 (Service Layer Mock)을 사용하여 실패한 4개 테스트를 재작성합니다. 이는 가장 빠르고 효과적인 해결 방법입니다.

**장기 계획**: Firebase Emulator 기반 통합 테스트를 별도로 구축하여 더 높은 신뢰도를 확보합니다.

---

**작성일**: 2025-11-08  
**테스트 통과율**: 92% (47/51)  
**목표**: 100% (51/51)

