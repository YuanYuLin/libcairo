import ops
import iopc

TARBALL_FILE="cairo-1.14.12.tar.xz"
TARBALL_DIR="cairo-1.14.12"
INSTALL_DIR="cairo-bin"
pkg_path = ""
output_dir = ""
tarball_pkg = ""
tarball_dir = ""
install_dir = ""
install_tmp_dir = ""
cc_host = ""
dst_include_dir = ""
dst_lib_dir = ""

def set_global(args):
    global pkg_path
    global output_dir
    global tarball_pkg
    global install_dir
    global install_tmp_dir
    global tarball_dir
    global cc_host
    global dst_include_dir
    global dst_lib_dir
    pkg_path = args["pkg_path"]
    output_dir = args["output_path"]
    tarball_pkg = ops.path_join(pkg_path, TARBALL_FILE)
    install_dir = ops.path_join(output_dir, INSTALL_DIR)
    install_tmp_dir = ops.path_join(output_dir, INSTALL_DIR + "-tmp")
    tarball_dir = ops.path_join(output_dir, TARBALL_DIR)
    cc_host_str = ops.getEnv("CROSS_COMPILE")
    cc_host = cc_host_str[:len(cc_host_str) - 1]
    dst_include_dir = ops.path_join(output_dir, ops.path_join("include",args["pkg_name"]))
    dst_lib_dir = ops.path_join(install_dir, "lib")

def MAIN_ENV(args):
    set_global(args)

    ops.exportEnv(ops.setEnv("CC", ops.getEnv("CROSS_COMPILE") + "gcc"))
    ops.exportEnv(ops.setEnv("CXX", ops.getEnv("CROSS_COMPILE") + "g++"))
    ops.exportEnv(ops.setEnv("CROSS", ops.getEnv("CROSS_COMPILE")))
    ops.exportEnv(ops.setEnv("DESTDIR", install_tmp_dir))

    #ops.exportEnv(ops.setEnv("LDFLAGS", ldflags))
    #ops.exportEnv(ops.setEnv("CFLAGS", cflags))
    #ops.exportEnv(ops.setEnv("LIBS", libs))
    
    #ops.exportEnv(ops.setEnv("LIBS", libs))
    #extra_conf.append('CFLAGS="-I' + ops.path_join(iopc.getSdkPath(), 'usr/include/libz') + '"')

    return False

def MAIN_EXTRACT(args):
    set_global(args)

    ops.unTarXz(tarball_pkg, output_dir)
    #ops.copyto(ops.path_join(pkg_path, "finit.conf"), output_dir)

    return True

def MAIN_PATCH(args, patch_group_name):
    set_global(args)
    for patch in iopc.get_patch_list(pkg_path, patch_group_name):
        if iopc.apply_patch(tarball_dir, patch):
            continue
        else:
            sys.exit(1)

    return True

def MAIN_CONFIGURE(args):
    set_global(args)

    cflags = iopc.get_includes()
    libs = iopc.get_libs()
    print cflags
    print libs
    print "SDK include path:" + iopc.getSdkPath()

    extra_conf = []
    extra_conf.append("--without-x")
    extra_conf.append("--enable-png=yes")
    extra_conf.append("--enable-xml=yes")
    extra_conf.append("--enable-glesv2=yes")
    extra_conf.append("--enable-drm=no") # TODO: need to fix
    extra_conf.append("--enable-ft=yes")
    extra_conf.append("--enable-fc=yes")
    extra_conf.append("--enable-gallium=no")
    extra_conf.append("--enable-egl=yes")
    extra_conf.append("--disable-ps") 
    extra_conf.append("--disable-pdf")
    extra_conf.append("--enable-svg=no")
    extra_conf.append("--enable-pthread=yes")
    extra_conf.append("--enable-gobject=yes")
    extra_conf.append("--enable-interpreter=no")
    extra_conf.append("--disable-gtk-doc")
    extra_conf.append("--host=" + cc_host)

    '''
    cflags = ""
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libpixman')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libpng')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/mesa')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libdrm')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libdrm/libdrm')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libudev')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/freetype')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/freetype/freetype2')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/fontconfig')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libz')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libxml2')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libglib')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libglib/glib-2.0')

    libs = ""
    libs += " -L" + ops.path_join(iopc.getSdkPath(), 'lib')
    libs += " -lpixman-1 -lpng -lGLESv2 -ldrm -lfreetype -lfontconfig -lEGL -lgbm -lexpat -lglapi -lffi -lz -lxml2 -lpthread -luuid"
    libs += " -lglib-2.0 -lwayland-client -lwayland-server -lpcre"
    '''
    extra_conf.append('pixman_CFLAGS=' + cflags)
    extra_conf.append('pixman_LIBS=' + libs)
    extra_conf.append('png_REQUIRES=libpng')
    extra_conf.append('png_CFLAGS=' + cflags)
    extra_conf.append('png_LIBS=' + libs)
    extra_conf.append('glesv2_CFLAGS=' + cflags)
    extra_conf.append('glesv2_LIBS=' + libs)
    extra_conf.append('drm_CFLAGS=' + cflags)
    extra_conf.append('drm_LIBS=' + libs)
    extra_conf.append('FREETYPE_CFLAGS=' + cflags)
    extra_conf.append('FREETYPE_LIBS=' + libs)
    extra_conf.append('FONTCONFIG_CFLAGS=' + cflags)
    extra_conf.append('FONTCONFIG_LIBS=' + libs)
    #extra_conf.append('egl_CFLAGS=-I' + ops.path_join(iopc.getSdkPath(), 'usr/include/mesa -I' + ops.path_join(iopc.getSdkPath(),'usr/include/libudev')) + ' -DMESA_EGL_NO_X11_HEADERS')
    extra_conf.append('egl_CFLAGS=' + cflags)
    extra_conf.append('egl_LIBS=' + libs)
    extra_conf.append('glib_CFLAGS=' + cflags)
    extra_conf.append('glib_LIBS=' + libs)
    extra_conf.append('CFLAGS=' + cflags)
    extra_conf.append('LIBS=' + libs)
    #extra_conf.append('CAIRO_CFLAGS=' + cflags)
    #extra_conf.append('CFLAGS=' + cflags)
    #libs = ""
    #libs += ' -L' + ops.path_join(iopc.getSdkPath(), 'lib') 
    #libs += ' -lz -lxml2 -lpthread -ldrm -luuid' 
    #extra_conf.append('CAIRO_LIBS=' + libs)
    #extra_conf.append('LIBS=' + libs)
    #extra_conf.append('egl_LIBS=-L' + ops.path_join(iopc.getSdkPath(), 'lib') + ' -lEGL -lgbm -ldrm -lexpat -lwayland-client -lglapi -lffi -lwayland-server')
    iopc.configure(tarball_dir, extra_conf)

    return True

def MAIN_BUILD(args):
    set_global(args)

    ops.mkdir(install_dir)
    ops.mkdir(install_tmp_dir)
    iopc.make(tarball_dir)
    iopc.make_install(tarball_dir)
    return True

def MAIN_INSTALL(args):
    set_global(args)

    ops.mkdir(install_dir)

    ops.mkdir(dst_lib_dir)

    libcairo = "libcairo.so.2.11400.12"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libcairo), dst_lib_dir)
    ops.ln(dst_lib_dir, libcairo, "libcairo.so.2")
    ops.ln(dst_lib_dir, libcairo, "libcairo.so")

    ops.mkdir(dst_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/cairo/cairo-deprecated.h"), dst_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/cairo/cairo-features.h"), dst_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/cairo/cairo.h"), dst_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/cairo/cairo-script.h"), dst_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/cairo/cairo-version.h"), dst_include_dir)

    iopc.installBin(args["pkg_name"], ops.path_join(ops.path_join(install_dir, "lib"), "."), "lib")
    iopc.installBin(args["pkg_name"], dst_include_dir, "include")

    return False

def MAIN_SDKENV(args):
    set_global(args)

    cflags = ""
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/' + args["pkg_name"])
    iopc.add_includes(cflags)

    libs = ""
    libs += " -lcairo"
    iopc.add_libs(libs)

    return False

def MAIN_CLEAN_BUILD(args):
    set_global(args)

    return False

def MAIN(args):
    set_global(args)

