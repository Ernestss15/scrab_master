import time
import cv2
import numpy as np
from letters import matrix_match

BOARD_SIZE = np.float32([[0, 0], [3000, 0], [0, 3000], [3000, 3000]])

def board_detection_BRISK(testImg):
    start = time.time()

    # Load and resize images
    refImg = cv2.imread('reference4.png', 0)
    colorTestImg = cv2.cvtColor(testImg, cv2.COLOR_RGB2BGR)
    testImg = cv2.cvtColor(testImg, cv2.COLOR_RGB2GRAY)

    if (testImg.size > 307200):
        testImg = cv2.resize(testImg, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        testImgBlur = cv2.blur(testImg, (5, 5))
        colorTestImg = cv2.resize(colorTestImg, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    if (refImg.size > 300000):
        refImg = cv2.resize(refImg, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        refImgBlur = cv2.blur(refImg, (5, 5))

    # Create BRISK, detect keypoints and descriptions
    brisk = cv2.BRISK_create(40)
    kp1, des1 = brisk.detectAndCompute(refImgBlur, None)
    kp2, des2 = brisk.detectAndCompute(testImgBlur, None)

    # Create BFMatcher and knnMatch descriptions
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    # Filter for only close enough matches
    good = []
    for m, n in matches:
        if m.distance < 0.65 * n.distance:
            good.append(m)

    # If there is enough matches warp the board, draw grid, find tiles and plot results
    if len(good) > 10:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()

        h, w = refImg.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)

        pts2 = np.float32([[0, 0], [w - 1, 0], [0, h - 1], [w - 1, h - 1]]).reshape(-1, 1, 2)
        dst2 = cv2.perspectiveTransform(pts2, M)
        img2 = cv2.polylines(testImg, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)

        draw_params = dict(matchColor=(0, 255, 0),
                           singlePointColor=None,
                           matchesMask=matchesMask,
                           flags=2)

        matrix = cv2.getPerspectiveTransform(dst2, BOARD_SIZE)
        warpped_board = cv2.warpPerspective(colorTestImg, matrix, (3000, 3000))

        tiles = detect_tiles(warpped_board)
        print("tiles : ", len(tiles))
        board_arr = matrix_match(tiles)

        print('\nfinished!')
        print('total time: ', time.time() - start)
		
		
		
        return board_arr.tolist()

    else:
        print('Not enough matches found!')

vertical_start = 207
horizontal_start = 180

def detect_tiles(refImg):
    refImg = cv2.cvtColor(refImg, cv2.COLOR_RGB2BGR)

    tiles = []

    h, w, r = refImg.shape

    width = int((w - 190) / 16 * 1)
    height = int((h - 645) / 16 * 1)

    start = [vertical_start, horizontal_start]

    min_letter_black = 5000
    min_letter = []
    max_non_letter_black = 0
    max_non_letter = []

    for i in range(0, 15):
        for j in range(0, 15):
            tile = refImg[start[1] + height * i: start[1] + height * (i + 1),
                   start[0] + width * j: start[0] + width * (j + 1)]

            tile_HSV = cv2.cvtColor(tile, cv2.COLOR_BGR2HSV)
            lower_black_HSV = np.array([0,0,0])
            upper_black_HSV = np.array([180,255,50])
            shapeMask_HSV = cv2.inRange(tile_HSV, lower_black_HSV, upper_black_HSV)

            maskHeightHSV = shapeMask_HSV.shape[0]
            maskWidthHSV = shapeMask_HSV.shape[1]

            black_pixels = 0
            white_pixels = 0
            for x in range(maskHeightHSV):
                for y in range(maskWidthHSV):
                    color = shapeMask_HSV[x,y]
                    if (color == 0):
                        shapeMask_HSV[x,y] = 255
                        # since inverted, this is white now
                        white_pixels += 1
                    elif (color == 255):
                        shapeMask_HSV[x,y] = 0
                        # since inverted, this is black now 
                        black_pixels += 1
                    else:
                        print("Should not get here")

            idx = [i,j]

            # skip center star for now as it causes issues (7,7)
            if (black_pixels > 1000 and idx != [7,7]):
                tiles.append(shapeMask_HSV)
            else:
                tiles.append(0)

    return tiles

def convert_image(image):
    """
    frame_raw = image.read()
    frame = np.array(bytearray(frame_raw), dtype=np.uint8)
    frame = cv2.imdecode(frame, -1)
    """
    board_arr = board_detection_BRISK(image)
	
	 #print(board_arr)
    return board_arr

