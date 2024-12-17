#!/bin/bash

# 프로젝트 이름 설정
PROJECT_NAME="./"

# 프로젝트 폴더 구조 생성
echo "📁 프로젝트 폴더와 파일을 생성합니다..."

# 프로젝트 루트 디렉토리 생성
mkdir -p ${PROJECT_NAME}/{configs,crawlers,common,pipelines,scheduler,logs,tests,utils}

# configs 디렉토리
touch ${PROJECT_NAME}/configs/{sites.yaml,database.yaml,crawler_settings.yaml}

# crawlers 디렉토리
touch ${PROJECT_NAME}/crawlers/{__init__.py,base_crawler.py,naver_crawler.py,daum_crawler.py}

# common 디렉토리
touch ${PROJECT_NAME}/common/{__init__.py,async_http_client.py,url_utils.py,selenium_utils.py,logger.py}

# pipelines 디렉토리
touch ${PROJECT_NAME}/pipelines/{__init__.py,data_cleaner.py,db_saver.py}

# scheduler 디렉토리
touch ${PROJECT_NAME}/scheduler/{__init__.py,scheduler.py}

# logs 디렉토리
touch ${PROJECT_NAME}/logs/{crawler.log,error.log}

# tests 디렉토리
touch ${PROJECT_NAME}/tests/{test_crawlers.py,test_pipeline.py}

# utils 디렉토리
touch ${PROJECT_NAME}/utils/{__init__.py,retry_handler.py,helpers.py}

# 프로젝트 루트에 메인 실행 파일과 의존성 관리 파일 생성
touch ${PROJECT_NAME}/{requirements.txt,main.py,README.md}

echo "✅ 프로젝트 폴더와 파일이 성공적으로 생성되었습니다!"
echo "💡 'cd ${PROJECT_NAME}' 명령어로 이동한 뒤 프로젝트 개발을 시작하세요."