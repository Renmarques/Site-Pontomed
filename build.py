# -*- coding: utf-8 -*-
"""Gera o site (pasta site/) a partir dos arquivos da pasta dados/.

Uso:  python build.py
Precisa so do Python 3 (nenhuma biblioteca extra).
"""
import os, runpy, sys

raiz = os.path.dirname(os.path.abspath(__file__))
sys.argv = [os.path.join(raiz, "ferramentas", "gerar_site.py"), os.path.join(raiz, "site")]
runpy.run_path(sys.argv[0], run_name="__main__")
