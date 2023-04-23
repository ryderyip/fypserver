from typing import Mapping

from qalib.models import Tag


class JsonTagExtractor:
    @staticmethod
    def extract(tag_jsons: list[Mapping[str, any]]) -> list[Tag]:
        l = []
        for tag_json in tag_jsons:
            tag, _ = Tag.objects.get_or_create(name=tag_json['name'])
            if tag.name != tag_json['name']:
                tag.update_tag(name=tag_json['name'])
            l.append(tag)
        return l
