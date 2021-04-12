import os
import cv2
import numpy as np
import uuid

from datetime import datetime
from contextlib import suppress
from typing import Union
from matplotlib import pyplot as plt

from django.conf import settings


def get_non_blank_frame(video_path: str) -> Union[np.ndarray, None]:
    last_analized_frame = None
    with suppress(Exception):
        cap = cv2.VideoCapture(video_path)

        cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)  # seek end
        number_of_frames = cap.get(cv2.CAP_PROP_POS_FRAMES)

        while number_of_frames >= 0:
            number_of_frames -= 1
            cap.set(cv2.CAP_PROP_POS_FRAMES, number_of_frames)
            ret, frame = cap.read()
            if not ret:
                break

            last_analized_frame = frame
            counts, bins = np.histogram(last_analized_frame)
            max_value = counts.max()
            sum_of_distribution_of_other_colors = sum(counts) - max_value

            if sum_of_distribution_of_other_colors > max_value:  # if there is no dominant color
                break

        cap.release()

    return last_analized_frame


def save_img(frame: Union[np.ndarray, None]):
    if frame is not None:
        random_sequence = str(uuid.uuid4())
        date = datetime.now()
        new_path = os.path.join(
            settings.MEDIA_ROOT, date.strftime('%Y'), date.strftime('%m'), date.strftime('%d'), 'disco'
        )
        os.makedirs(os.path.join(f'{settings.MEDIA_ROOT}', new_path), exist_ok=True)
        plt.imsave(os.path.join(new_path, f"{random_sequence}-last_non_blank_frame.jpg"), frame)


def extract_last_non_blank_frame(video_path: str):
    frame = get_non_blank_frame(video_path)
    save_img(frame)
