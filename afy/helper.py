import face_alignment


def extract_bbox(frame, fa, increase_area=0.1):
    frame_shape = frame.shape
    
    if max(frame.shape[0], frame.shape[1]) > 640:
        scale_factor =  max(frame.shape[0], frame.shape[1]) / 640.0
        frame = resize(frame, (int(frame.shape[0] / scale_factor), int(frame.shape[1] / scale_factor)))
        frame = img_as_ubyte(frame)
    else:
        scale_factor = 1
    frame = frame[..., :3]
    bboxes = fa.face_detector.detect_from_image(frame[..., ::-1])
    if len(bboxes) == 0:
        return []
    
#     assert len(bboxes) == 1
    bbox = np.array(bboxes)[0, :-1] * scale_factor
    
#     return bbox

    left, top, right, bot = bbox
    width = right - left
    height = bot - top

    #Computing aspect preserving bbox
    width_increase = max(increase_area, ((1 + 2 * increase_area) * height - width) / (2 * width))
    height_increase = max(increase_area, ((1 + 2 * increase_area) * width - height) / (2 * height))

    left = int(left - width_increase * width)
    top = int(top - height_increase * height)
    right = int(right + width_increase * width)
    bot = int(bot + height_increase * height)

    
#     top, bot, left, right = max(0, top), min(bot, frame_shape[0]), max(0, left), min(right, frame_shape[1])
    
    return left, top, right, bot


def overlay(background, result, offset):
    background = deepcopy(background)
    background = np.array(background)[..., :3]
    mask = make_overlay_mask()[:, :, np.newaxis]
    background[offset[0]:offset[0]+256, offset[1]:offset[1]+256] = \
        background[offset[0]:offset[0]+256, offset[1]:offset[1]+256] * (1 - mask) + \
        np.array(result)[..., :3] * mask
    
    return Image.fromarray(background.astype(np.uint8))


