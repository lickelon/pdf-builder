from modules.kice_cropper import KiceCropper
if __name__ == '__main__':
    kc = KiceCropper()
    kc.extract_problems_to_original('input/2025학년도 대수능.pdf', 10)