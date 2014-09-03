" source $VIMRUNTIME/vimrc_example.vim

syntax on
set ruler
set background=dark
filetype on
filetype plugin indent on

" remember the last cursor position
autocmd BufReadPost *
  \ if line("'\"") > 1 && line("'\"") <= line("$") |
  \   exe "normal! g`\"" |
  \ endif

" the following line sets the indentation and column width for python files
" ts, et, sw, sts, ai are abbreviations for tabstop, expandtab, shiftwidth
" softtabstop, autoindent respectively
autocmd FileType python set number columns=80 ts=4 et sw=4 sts=4 ai
