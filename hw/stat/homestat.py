#!/usr/bin/env python3
from typing import Optional

import gender_guesser.detector as gender
import translators as ts

Stat = dict[str, list[dict[str, str]]]
detector = gender.Detector(case_sensitive=False)


def translate_to_en(text: str) -> str:
    return ts.translate_text(text, to_language="en")


def is_male(name: str) -> bool:
    return detector.get_gender(translate_to_en(name)) in [
        "male",
        "mostly_male",
    ] or name.lower() in ["ильгиз", "вачаган", "ленар"]


def is_female(name: str) -> bool:
    return detector.get_gender(translate_to_en(name)) in [
        "female",
        "mostly_female",
    ] or name.lower() in ["любовь"]


def make_stat(filename: str) -> Stat:
    """
    Функция вычисляет статистику по именам за каждый год с учётом пола.
    """
    with open(filename, "rb") as handle:
        text = handle.read().decode("cp1251")

    stat: Stat = {}

    part_of_table: str = text.split("<tbody>")[1]
    rows_table: list[str] = part_of_table.split("</tr>")[:-1]
    current_year: Optional[str] = None
    for row in rows_table:
        if "h3" in row:
            # Нашли год
            start = row.index("h3") + 3
            year = row[start : start + 4]

            current_year = year
            stat[current_year] = []
        elif "a" in row:
            # Нашли строчку имени
            full_name = row.split('">')[-1].replace("</a></td>", "").split(" ")
            full_name = {"name": full_name[1], "surname": full_name[0]}
            stat[current_year].append(full_name)
        else:
            print(f"Unknown row: {row}")

    return stat


def extract_years(stat: Stat) -> list[str]:
    """
    Функция принимает на вход вычисленную статистику и выдаёт список годов,
    упорядоченный по возрастанию.
    """
    return sorted(stat.keys())


def extract_general(stat: Stat, year_view: bool = False):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для всех имён.
    Список должен быть отсортирован по убыванию количества.
    """
    names_stat: dict[str, int] = {}
    year_stat: dict[str, list[tuple]] = {}

    def mini_stat_to_list(mini_stat: dict[str, int]):
        return sorted(mini_stat.items(), key=lambda x: x[1], reverse=True)

    for year_value in stat:
        year: list[dict[str, str]] = stat[year_value]
        year_names_stat: dict[str, int] = {}
        for full_name in year:
            if full_name["name"] not in names_stat:
                names_stat[full_name["name"]] = 0
            if full_name["name"] not in year_names_stat:
                year_names_stat[full_name["name"]] = 0

            names_stat[full_name["name"]] += 1
            year_names_stat[full_name["name"]] += 1

        year_stat[year_value] = mini_stat_to_list(year_names_stat)

    if not year_view:
        return mini_stat_to_list(names_stat)
    else:
        return year_stat


def extract_general_male(stat: Stat, year: str = None):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для имён мальчиков.
    Список должен быть отсортирован по убыванию количества.
    """
    if not year:
        stat = extract_general(stat)
    else:
        stat = extract_year(stat, year)
    male_stat = []
    for name_stat in stat:
        if is_male(name_stat[0]):
            male_stat.append(name_stat)
    return male_stat


def extract_general_female(stat: Stat, year: str = None):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для имён девочек.
    Список должен быть отсортирован по убыванию количества.
    """
    if not year:
        stat = extract_general(stat)
    else:
        stat = extract_year(stat, year)
    female_stat = []
    for name_stat in stat:
        if is_female(name_stat[0]):
            female_stat.append(name_stat)
    return female_stat


def extract_year(stat: Stat, year: str):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    return extract_general(stat, year_view=True)[year]


def extract_year_male(stat: Stat, year: str):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён мальчиков в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    return extract_general_male(stat, year)


def extract_year_female(stat: Stat, year: str):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён девочек в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    return extract_general_female(stat, year)


if __name__ == "__main__":
    pass
