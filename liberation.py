import time
import requests
from bs4 import BeautifulSoup
from PIL import Image
from pillow_lut import load_cube_file

CAM_FOLDER = "116_PANA"
CAM_FOLDER = "100_FUJI"

BASE_DIR = "DCIM%5C" + CAM_FOLDER
STORE_TO = "DCIM/" + CAM_FOLDER

LUTS ="""
filmist_classic_neg.cube
filmist_agfaflex.cube
filmist_portra.cube
punk/Bonus - Satin.cube
punk/Electric.cube
punk/Grim.cube
punk/Grit.cube
punk/Intense Colors.cube
punk/Just Cyberpunk.cube
punk/Moody O+T.cube
punk/Muted Blue.cube
punk/Vivid City.cube
punk/Vivid City II.cube
""".strip().splitlines()

LUTS ="""
filmist_classic_neg.cube
punk/Vivid City II.cube
""".strip().splitlines()

LUTS = ["neg.cube", "ptra.cube"]


LUTS ="""
neg.cube
ptra.cube
punk/Bonus - Satin.cube
punk/Electric.cube
punk/Grim.cube
punk/Just Cyberpunk.cube
punk/Vivid City II.cube
""".strip().splitlines()

# globals
LAST_FILELIST = None

def apply_to_file(file_name):
    im = Image.open(file_name)
    exif = im.info['exif']
    im_root = file_name.split(".")[0]
    output_files = []
    for lut_file in LUTS:
        print("Applying LUT", lut_file, "to file", file_name)
        lut = load_cube_file(lut_file)
        file_no = int(file_name.split(".JPG")[0][-3:])
        print("FILE NO", file_no)
        output_filename = str("%03d" % (999 - file_no))
        output_filename = "output/%03d-%s.jpg" % (file_no, lut_file.split(".")[0].replace("/", "-"))
        output_filename = output_filename.replace("-", "").replace("_", "").replace(" ", "")
        im.filter(lut).save(output_filename, exif=exif)
        output_files.append(output_filename)
    return output_files

def upload_file_to_cam(file):
    base_file_name = file.split("/")[-1]
    files = {'file': (base_file_name, open(file, 'rb').read()),
    }
    data = {
        'time': "2023:1:20:18:44:56",
        'save-as-filename': '/' + STORE_TO + "/" + base_file_name,
        'StrLJ': base_file_name
    }
    data = {
        'save-as-filename': '/' + STORE_TO + "/" + base_file_name,
    }
    request = requests.Request("POST","http://192.168.4.1/upload",files=files,data=data)
    prepared = request.prepare()
    print("Uploading", file)
    s = requests.Session()
    s.send(prepared)


def get_latest_file():
    global LAST_FILELIST
    page = requests.get("http://192.168.4.1/dir?dir=" + BASE_DIR)
    print(BASE_DIR)
    soup = BeautifulSoup(page.text, 'html.parser')
    all_links = soup.find_all("a")
    all_links = [x.text.strip() for x in all_links][2:]
    dscf_links = []
    for link in all_links:
        if "DSCF" in link:
            dscf_links.append(link)
    all_links = dscf_links
    if LAST_FILELIST is None:
        new_links = []
    else:
        if len(LAST_FILELIST) >= len(all_links):
            return
        new_links = set(all_links) - set(LAST_FILELIST)
    LAST_FILELIST = all_links
    print("Filelist", LAST_FILELIST)
    print("new links", new_links)
    for file in new_links:
        r = requests.get("http://192.168.4.1/download?file=" + BASE_DIR + "%5C" + file, allow_redirects=True)
        print("http://192.168.4.1/download?file=" + BASE_DIR + "%5C" + file)
        open('output/' + file, 'wb').write(r.content)
        print("Downloaded new file", file)
        output_files = apply_to_file("output/" + file)
        print("Output files", output_files)
        for file in output_files:
            upload_file_to_cam(file)
        print("DONE UPLOADING FILM SIMS")

while True:
    get_latest_file()
    time.sleep(5)
apply_to_file("input.jpg")

