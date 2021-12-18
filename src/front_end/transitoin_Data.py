import json
s = json.load(open("result.json"))
# print(s)
def search(target):
    for data in s["data"]:
        id = data["id"]
        gtImg = data["gtImg"]
        if gtImg.find(target) != -1:
            print(id)
            print(data["class"])

search("e09c32b947e33f619ba010ddb4974fe")
search("cd94233033b1d958ef2438b4b778b7f8")

search("cdfd278e8b1c11bfc36d58d0f13497a0")

search("fa0a32c4326a42fef51f77a6d7299806")

search("e389a5eaaa448a00d6bd2821a9079b28")
intp_ids = [169, 805, 234, 587, 778]
intp_class_id = ["02691156", "04379243",
 "03001627", "03636649", "04256520"]
intp_ids = [169, 587, 805, 778, 234]
intp_class_id = ["02691156", "03636649", "04379243", "04256520",
 "03001627", ]
trans = []
for i in range(5):
    j = (i + 1) % 5
    sourceId = intp_ids[i]
    targetId = intp_ids[j]
    frames = []
    for k in range(99):
        sourceWeight = (k + 1) / 101
        img = "picture/png_interpolation_all/" + \
            intp_class_id[i] + '_to_' + intp_class_id[j] +'/'+\
                str(k) + '.png'
        frame = {
            "frame": k,
            "sourceWeight": sourceWeight,
            "img": img
        }
        frames.append(frame)

    transition = {
        "frames":frames,
        "sourceId": sourceId,
        "targetId":targetId
    }
    trans.append(transition)

json.dump({"transitions":trans}, open("trans.json", 'w'))