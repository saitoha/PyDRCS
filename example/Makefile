
VIMRUNTIME=~/.vim
FTDETECTDIR=$(VIMRUNTIME)/ftdetect
FTPLUGINDIR=$(VIMRUNTIME)/ftplugin

all: $(FTDETECTDIR) $(FTPLUGINDIR)
	ln -f vim/ftdetect/drcs.vim $(FTDETECTDIR)
	ln -f vim/ftdetect/image.vim $(FTDETECTDIR)
	ln -f vim/ftplugin/drcs.vim $(FTPLUGINDIR)
	ln -f vim/ftplugin/image.vim $(FTPLUGINDIR)

$(FTDETECTDIR):
	mkdir -p $@

$(FTPLUGINDIR):
	mkdir -p $@
