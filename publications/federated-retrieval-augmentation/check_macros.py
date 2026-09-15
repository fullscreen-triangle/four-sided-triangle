import re

content = open('federated-retrieval-augmentation.tex', encoding='utf-8').read()

defined = set(re.findall(r'\\newcommand\{\\([a-zA-Z]+)\}', content))
defined |= set(re.findall(r'\\DeclareMathOperator\*?\{\\([a-zA-Z]+)\}', content))

builtin = set('''begin end label ref cref Cref citep cite item section subsection
subsubsection paragraph title author date maketitle documentclass usepackage
newtheorem newtheoremstyle theoremstyle crefname Crefname part tableofcontents
bibliography bibliographystyle includegraphics caption centering textwidth
linewidth toprule midrule bottomrule small textbf emph texttt noindent vspace
leftmargin itemsep footnote hline multicolumn newcommand DeclareMathOperator
mathbb mathcal mathsf mathrm mathit mathbf lVert rVert lvert rvert dfrac frac
sum prod min max inf sup log exp sin cos left right big Big bigl bigr Bigl Bigr
quad qquad text emptyset varnothing notin in subseteq subsetneq supsetneq neq
leq geq le ge times cdot cdots ldots dots vdots ddots infty forall exists
partial nabla to mapsto rightarrow Rightarrow iff Leftrightarrow wedge vee neg
lnot langle rangle lfloor rfloor lceil rceil hat bar tilde vec dot ddot
overline underline sqrt binom choose pmod bmod equiv sim simeq approx propto
perp parallel angle triangle square circ bullet star ast pm mp setminus cup
cap uplus sqcup sqcap oplus otimes top bot aleph hbar ell wp Re Im
prime backslash colon vert Vert
hypersetup multirow arraystretch resizebox scalebox includepdf appendix
printbibliography addbibresource declaretheorem declaretheoremstyle
Crefname enumerate itemize description array booktabs graphicx algorithm
algpseudocode natbib hyperref cleveref xcolor microtype mathtools mathrsfs bm
lmodern fontenc inputenc geometry amsmath amssymb amsthm colorlinks linkcolor
citecolor urlcolor round sort compress State Statex Require Ensure Function
EndFunction algorithmic'''.split())

used = set(re.findall(r'\\([a-zA-Z]{2,})', content))

missing = sorted(u for u in used if u not in defined and u not in builtin)
print(len(missing), 'candidates')
for m in missing:
    print(m)
