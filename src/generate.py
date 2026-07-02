import os
import shutil
from os.path import isfile

from htmlnode import HTMLNode
from markdown_to_html import extract_title, markdown_to_html_node


def generate(public_dir: str, static_dir: str):
    public_dir_abs: str = os.path.abspath(public_dir)
    if os.path.exists(public_dir_abs):
        shutil.rmtree(public_dir_abs)

    static_dir_abs: str = os.path.abspath(static_dir)
    if not os.path.exists(static_dir_abs):
        raise ValueError("static dir does not exists")

    os.mkdir(public_dir_abs)

    cp_static_to_public(public_dir_abs, static_dir_abs)


def generate_pages_recursive(
    basepath: str, dir_path_content: str, template_path: str, dest_dir_path: str
):
    dir_path_content_abs: str = os.path.abspath(dir_path_content)
    template_path_abs: str = os.path.abspath(template_path)
    dest_dir_path_abs: str = os.path.abspath(dest_dir_path)

    entries: list[str] = os.listdir(dir_path_content_abs)
    print(entries)

    for entry in entries:
        entry_abs: str = os.path.join(dir_path_content, entry)
        if os.path.isfile(entry_abs):
            dest_html_abs: str = os.path.join(
                dest_dir_path_abs, entry.replace(".md", ".html")
            )
            generate_page(basepath, entry_abs, template_path_abs, dest_html_abs)
        else:
            public_subdir_abs: str = os.path.join(dest_dir_path_abs, entry)
            generate_pages_recursive(
                basepath, entry_abs, template_path_abs, public_subdir_abs
            )


def generate_page(basepath: str, from_path: str, template_path: str, dest_path: str):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    from_path_abs: str = os.path.abspath(from_path)
    template_path_abs: str = os.path.abspath(template_path)
    dest_path_abs: str = os.path.abspath(dest_path)
    md: str = ""
    tmpl: str = ""
    html: str = ""
    title: str = ""
    with open(from_path_abs) as f:
        md = f.read()
    with open(template_path_abs) as t:
        tmpl = t.read()

    html_node: HTMLNode = markdown_to_html_node(md)
    html = html_node.to_html()
    title = extract_title(md)
    tmpl = tmpl.replace("{{ Title }}", title)
    tmpl = tmpl.replace("{{ Content }}", html)
    tmpl = tmpl.replace('href="/', f'href="{basepath}')
    tmpl = tmpl.replace('src="/', f'src="{basepath}')
    public_path = os.path.dirname(dest_path_abs)
    if not os.path.exists(public_path):
        os.makedirs(public_path)

    with open(dest_path_abs, "w") as d:
        d.write(tmpl)


def cp_static_to_public(public_dir_abs: str, static_dir_abs: str):
    entries: list[str] = os.listdir(static_dir_abs)
    for entry in entries:
        entry_abs: str = os.path.join(static_dir_abs, entry)
        if os.path.isfile(entry_abs):
            shutil.copy(entry_abs, public_dir_abs)
        else:
            public_subdir_abs: str = os.path.join(public_dir_abs, entry)
            os.mkdir(public_subdir_abs)
            cp_static_to_public(public_subdir_abs, entry_abs)
