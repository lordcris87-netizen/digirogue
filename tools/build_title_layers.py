"""Build independent title characters from the original flattened cover.

Development-only prototype. The source art remains unchanged; generated assets
must be reviewed before release. Run: python tools/build_title_layers.py
Requires pillow, numpy and opencv-python-headless.
"""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ASSETS / "title_layers"
OUT.mkdir(exist_ok=True)
scene = np.asarray(Image.open(ASSETS / "portada.webp").convert("RGB"))
height, width = scene.shape[:2]

# Outlines manually traced over the source at 1672 x 941. Additional GrabCut
# refinement is applied to avoid bringing tree and vegetation into the layers.
SHAPES = {
    "agumon": ((0,493,298,790), """
        13,679 20,675 38,691 47,699 80,697 92,658 113,624 107,594
        105,560 121,538 145,507 188,502 210,504 236,503 268,498
        286,517 290,544 273,557 279,578 268,599 264,626 236,633
        240,661 254,686 267,712 281,735 292,755 289,774 257,779
        213,777 172,782 132,783 95,770 67,747 31,731 18,715
    """),
    "gabumon": ((228,509,503,814), """
        236,701 268,670 274,627 295,613 284,582 276,567 297,569
        335,582 339,562 344,555 340,544 336,539 355,557 372,568
        391,575 410,576 412,547 420,514 429,516 432,550 440,576
        446,582 472,598 478,613 477,640 455,650 439,656 431,674
        436,702 451,719 466,734 488,758 497,772 475,787 455,792
        422,796 403,808 370,806 343,795 316,793 302,770 273,768
        268,747 245,732
    """),
    "bat": ((1213,84,1418,215), """
        1219,98 1239,97 1264,89 1289,87 1308,93 1322,102 1341,123
        1355,139 1367,111 1370,107 1390,126 1401,149 1400,155
        1412,171 1412,192 1402,198 1391,207 1366,206 1346,195
        1330,175 1307,164 1297,152 1284,148 1268,142 1246,121
    """),
    "bird": ((1425,509,1601,717), """
        1430,609 1439,597 1451,578 1466,564 1484,553 1497,545
        1495,523 1517,513 1534,522 1543,544 1559,545 1578,546
        1590,546 1573,572 1581,583 1571,601 1593,629 1567,643
        1565,665 1583,678 1591,686 1590,698 1580,704 1556,698
        1532,703 1525,710 1492,705 1480,695 1462,686 1455,672
        1457,650 1446,643 1439,630
    """),
}
all_masks = []
metadata = {}
for name, (box, raw_points) in SHAPES.items():
    x0,y0,x1,y1 = box
    points = np.array([tuple(map(int,p.split(","))) for p in raw_points.split()], np.int32)
    outline = np.zeros((height,width),np.uint8)
    cv2.fillPoly(outline,[points],255)
    wide = cv2.dilate(outline,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(17,17)))
    core = cv2.erode(outline,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
    seed = np.full((height,width),cv2.GC_BGD,np.uint8)
    seed[wide>0] = cv2.GC_PR_BGD
    seed[outline>0] = cv2.GC_PR_FGD
    seed[core>0] = cv2.GC_FGD
    crop = scene[y0:y1,x0:x1]
    working = seed[y0:y1,x0:x1].copy()
    cv2.grabCut(cv2.cvtColor(crop,cv2.COLOR_RGB2BGR),working,None,
                np.zeros((1,65),np.float64),np.zeros((1,65),np.float64),
                6,cv2.GC_INIT_WITH_MASK)
    alpha = np.isin(working,[cv2.GC_FGD,cv2.GC_PR_FGD]).astype(np.uint8)*255
    hsv = cv2.cvtColor(crop,cv2.COLOR_RGB2HSV)
    if name in ("agumon","bat","bird"):
        if name == "bird":
            dominant = cv2.inRange(hsv,(128,55,68),(179,255,255))
            radius=35
        else:
            dominant = cv2.inRange(hsv,(4,90,100),(35,255,255))
            radius=29
        dominant = cv2.morphologyEx(dominant,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
        n,labels,stats,_ = cv2.connectedComponentsWithStats(dominant)
        if n>1:
            biggest = 1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
            dominant=(labels==biggest).astype(np.uint8)*255
            near=cv2.dilate(dominant,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(radius,radius)))
            alpha=cv2.bitwise_and(alpha,near)
    if name=="gabumon":
        # Green vegetation is not part of the blue-white character.
        is_green=(hsv[:,:,0]>=34)&(hsv[:,:,0]<90)&(hsv[:,:,1]>65)
        alpha[is_green]=0
    alpha=cv2.morphologyEx(alpha,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    rgba=np.dstack((crop,alpha))
    Image.fromarray(rgba,"RGBA").save(OUT/(name+".png"),optimize=True)
    full=np.zeros((height,width),np.uint8)
    full[y0:y1,x0:x1]=alpha
    all_masks.append(full)
    metadata[name]={"box":list(box),"pixels":int(np.count_nonzero(alpha))}
    print(name,metadata[name])

# Cover every removed character pixel. The generated background is a temporary
# underpainting: only a few pixels at the silhouettes are meant to be exposed
# during the subtle idle animations. It is not standalone environment art.
remove=cv2.dilate(np.maximum.reduce(all_masks),np.ones((7,7),np.uint8))
bgr=cv2.cvtColor(scene,cv2.COLOR_RGB2BGR)
inpainted=cv2.inpaint(bgr,remove,7,cv2.INPAINT_TELEA)
Image.fromarray(cv2.cvtColor(inpainted,cv2.COLOR_BGR2RGB)).save(
    OUT/"background.webp",quality=94,method=6)
import json
(OUT/"manifest.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
