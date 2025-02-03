import os
import re
import time
import pythoncom
import win32com.client as win32
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from utils.overlay_object import *
from utils.parse_code import *
from utils.coord import Coord
from utils.ratio import Ratio
import fitz

hwp_lock = Lock()

def code2path(item_code):
    section = parse_code(item_code)["section"]
    topic = parse_code(item_code)["topic"]
    if section == 'KC':
        item_path = 'T:/THedu/KiceDB'
    else:
        item_path = 'T:/THedu/ItemDB'
    hwp_path = os.path.join(item_path, topic, item_code, f"{item_code}.hwp")
    pdf_path = hwp_path.replace('.hwp', '.pdf')
    return hwp_path, pdf_path

def convert_hwp_to_pdf(item_code):
    """HWP를 PDF로 변환하는 함수"""
    hwp_path, pdf_path = code2path(item_code)

    try:
        # 1) HWP와 PDF 파일 존재 여부 및 생성 시간 체크
        if os.path.exists(hwp_path) and os.path.exists(pdf_path):
            hwp_time = os.path.getctime(hwp_path)
            pdf_time = os.path.getctime(pdf_path)

            # PDF가 HWP보다 나중에 생성되었다면 변환 불필요
            if pdf_time > hwp_time:
                pdf_size = os.path.getsize(pdf_path)
                # PDF 크기가 10KB 초과면 기존 PDF 사용
                if pdf_size > 10 * 1024:
                    return pdf_path

        # 2) PDF 변환 시도 (최대 3회)
        for attempt in range(3):
            pythoncom.CoInitialize()
            try:
                with hwp_lock:
                    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
                    hwp.XHwpWindows.Item(0).Visible = False
                    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule") #보안 모듈 pass
                    hwp.Open(hwp_path)
                    hwp.XHwpDocuments.Item(0).XHwpPrint.filename = pdf_path
                    hwp.XHwpDocuments.Item(0).XHwpPrint.RunToPDF()
                    time.sleep(0.5)  # PDF 변환 완료 대기

                # PDF 파일 크기 확인
                if os.path.exists(pdf_path):
                    pdf_size = os.path.getsize(pdf_path)
                    if pdf_size > 10 * 1024:  # 10KB 초과면 성공
                        return pdf_path
                    elif attempt == 2:  # 마지막 시도였다면
                        return pdf_path  # 크기가 작아도 반환

            except Exception as e:
                if attempt == 2:  # 마지막 시도에서 실패
                    return None

            finally:
                if hwp:
                    try:
                        hwp.Quit()
                    except:
                        pass
                pythoncom.CoUninitialize()

            # 다음 시도 전 잠시 대기
            time.sleep(1)

    except Exception as e:
        return None

def create_pdfs(item_codes):
    total_files = len(item_codes)
    completed = 0

    # CPU 코어 수를 고려하여 최적의 worker 수 결정
    # HWP 변환은 리소스를 많이 사용하므로 worker 수를 제한
    max_workers = min(os.cpu_count() // 2 or 1, 2)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(convert_hwp_to_pdf, file): file
            for file in item_codes
        }

        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                pdf_path = future.result()
                if pdf_path:
                    completed += 1
                    progress = int((completed / total_files) * 100)
                    print(f"Progress: {progress}% - Converted: {os.path.basename(file)}")
            except Exception as e:
                print(f"Error processing {file}: {str(e)}")
