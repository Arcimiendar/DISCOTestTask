import os
import cv2
import numpy as np
import uuid
import logging
import re

from datetime import datetime
from contextlib import suppress
from typing import Union, List
from itertools import combinations
from matplotlib import pyplot as plt

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


logger = logging.getLogger(__name__)


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
        new_path = default_storage.path(
            f"temp_folder/{date.strftime('%Y')}, {date.strftime('%m')}, {date.strftime('%d')}"
        )

        os.makedirs(os.path.join(new_path), exist_ok=True)
        plt.imsave(os.path.join(new_path, f"{random_sequence}-last_non_blank_frame.jpg"), frame)


def extract_last_non_blank_frame(video_path: str):
    frame = get_non_blank_frame(video_path)
    save_img(frame)


def get_all_possible_word_truncation_indices(words):
    words_indices = list(range(len(words)))

    def count_how_many_sequencial_numbers(combination):
        if combination[0] != 0:
            return -1
        elif combination[-1] != len(words) - 1:
            return -1
        count = 0
        iterator = iter(combination)
        prev_element = next(iterator)
        for element in iterator:
            if element - 1 == prev_element:
                count += 1
            prev_element = element
        return count

    valid_combinations = []
    for i in range(2, len(words)):
        combins = filter(
            lambda combination: i - 2 == count_how_many_sequencial_numbers(combination), combinations(words_indices, i)
        )
        valid_combinations.extend(combins)
    return valid_combinations


def create_truncation_from_indices(delimeters, words, indices):
    word_accumulator = delimeters[0]
    index_iter = iter(indices)
    prev_index = next(index_iter)
    word_accumulator += words[prev_index] + delimeters[prev_index + 1]

    for index in index_iter:
        if prev_index + 1 != index:
            word_accumulator += '...' + delimeters[index]
        word_accumulator += words[index] + delimeters[index + 1]
        prev_index = index

    return word_accumulator


def get_all_possible_truncations(str_sequence: str) -> List[str]:
    delimeters = re.split(r'[A-Za-z0-9]+', str_sequence)  # don't use \w because "_" is separator too
    words = re.split(r'[^A-Za-z0-9]+', str_sequence)

    if len(words) <= 2:
        return [str_sequence]

    valid_combinations = get_all_possible_word_truncation_indices(words)

    all_possible_truncations = []
    for word_indices in valid_combinations:
        all_possible_truncations.append(create_truncation_from_indices(delimeters, words, word_indices))
    all_possible_truncations.append(str_sequence)
    return all_possible_truncations


def combine_paths(all_truncations, max_length, level=0, previous_path=''):
    if level >= len(all_truncations):
        return previous_path

    current_truncation_layer = all_truncations[level]
    last_succesfull_truncation = ''
    for truncation in current_truncation_layer:
        path = os.path.join(previous_path, truncation)
        path = combine_paths(all_truncations, max_length, level + 1, path)
        if path is None:
            continue

        if len(path) > max_length:
            continue

        if len(last_succesfull_truncation) < len(path):
            last_succesfull_truncation = path

    if last_succesfull_truncation == '':
        return None

    return last_succesfull_truncation


def truncate_filename(old_filename: str, max_filename_length: int) -> Union[str, None]:
    if len(old_filename) < max_filename_length:
        logger.info(f'filename {old_filename} does not need to be truncated')
    path_parts = re.split(r'[\\/]', old_filename)
    path_prefix, end_filename = list(path_parts[:-1]), path_parts[-1]
    max_filename_length -= len(path_prefix) + 1  # +1 for delimeter

    filename, extenstion = os.path.splitext(end_filename)
    max_filename_length -= len(extenstion)
    path_prefix.append(filename)

    all_combination_part = list(map(lambda path_part: get_all_possible_truncations(path_part), path_prefix))

    truncation = combine_paths(all_combination_part, max_filename_length)

    # valid_combination
    if truncation is None:
        logger.warning(f'truncation for {old_filename} with length {max_filename_length} is not possible')
        return None

    return truncation + extenstion
