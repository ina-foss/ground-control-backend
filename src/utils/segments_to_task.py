import json



def convert(segments, video_id):
    # json.dumps({'data': segments, 'predictions': []})
    with open("tasks.json", 'w') as file:
        json.dump({'data': segments, 'predictions': []}, file)
