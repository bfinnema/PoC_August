all:	fxs

# Include standard NCS examples build definitions and rules
include $(NCS_DIR)/src/ncs/build/include.ncs.mk

SRC = $(wildcard yang/*.yang)
FXS = $(SRC:yang/%.yang=../load-dir/%.fxs)

fxs:	$(FXS)

../load-dir:
	mkdir $@

../python/_namespaces:
	mkdir -p $@

../load-dir/%.fxs:	yang/%.yang ../load-dir ../python/_namespaces
	$(NCSC)  `ls $*-ann.yang  > /dev/null 2>&1 && echo "-a $*-ann.yang"` \
             $(YANGPATH) -c -o $@ $<
	$(NCSC) --emit-python ../python/_namespaces/$(notdir $(basename $<)).py $@

clean:
	rm -rf  ../load-dir/* ../python/_namespaces/*.py
	rm -rf  ./src/*/*.pyc
