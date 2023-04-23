from typing import Mapping

from qalib.models import ContentBlockCommonInfo, ContentBlockContainer, ImageBlock, LatexBlock, TextBlock


class ContentBlockUpdateOrCreator:
    def __init__(self, block_info: ContentBlockCommonInfo):
        self.block_info = block_info

    def uoc_text_block(self, text: str):
        if self.block_info.type != ContentBlockCommonInfo.BlockType.TEXT:
            raise Exception('wrong content block type')
        b, created = TextBlock.objects.update_or_create(info=self.block_info, defaults={'text': text, 'info': self.block_info})

    def uoc_latex_block(self, latex: str):
        if self.block_info.type != ContentBlockCommonInfo.BlockType.LATEX:
            raise Exception('wrong content block type')
        LatexBlock.objects.update_or_create(info=self.block_info, defaults={'latex': latex, 'info': self.block_info})

    def uoc_image_block(self, image_name: str):
        if self.block_info.type != ContentBlockCommonInfo.BlockType.IMAGE:
            raise Exception('wrong content block type')
        ImageBlock.objects.update_or_create(info=self.block_info, defaults={'image_name': image_name, 'info': self.block_info})


def update_or_create_content_block(block_info: ContentBlockCommonInfo, json_block):
    # [{'info': {'type': 'txt', 'ordering': 1}, 'text': '(question)'}]
    updater = ContentBlockUpdateOrCreator(block_info)
    if block_info.type == ContentBlockCommonInfo.BlockType.TEXT:
        updater.uoc_text_block(json_block['text'])
    elif block_info.type == ContentBlockCommonInfo.BlockType.IMAGE:
        updater.uoc_image_block(json_block['image_name'])
    elif block_info.type == ContentBlockCommonInfo.BlockType.LATEX:
        updater.uoc_latex_block(json_block['latex'])
    else:
        print('unknown block type !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')


class ContentBlockUOCHandler:
    @staticmethod
    def uoc(content_container: ContentBlockContainer, json: Mapping[str, any]):
        # clear all, then add blocks to empty container
        content_container.blocks.all().delete()

        content_blocks_in_json = json['content_blocks']
        for i, json_block in enumerate(content_blocks_in_json):
            json_block_info = json_block['info']
            block_info = ContentBlockCommonInfo.objects.create(
                type=json_block_info['type'],
                content_container=content_container,
                ordering=i+1,
            )
            update_or_create_content_block(block_info, json_block)
