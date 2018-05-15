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

    cc_sysroot = ops.getEnv("CC_SYSROOT")

    cflags = ""
    cflags += " -I" + ops.path_join(cc_sysroot, 'usr/include')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libz') 

    ldflags = ""
    ldflags += " -L" + ops.path_join(cc_sysroot, 'lib')
    ldflags += " -L" + ops.path_join(cc_sysroot, 'usr/lib')
    ldflags += " -L" + ops.path_join(iopc.getSdkPath(), 'lib')

    libs = ""
    libs += " -lpixman-1 -lpng -lz"

    ops.exportEnv(ops.setEnv("LDFLAGS", ldflags))
    ops.exportEnv(ops.setEnv("CFLAGS", cflags))
    ops.exportEnv(ops.setEnv("LIBS", libs))
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

    print "SDK include path:" + iopc.getSdkPath()

    extra_conf = []
    extra_conf.append("--without-x")
    extra_conf.append("--enable-png=yes")
    extra_conf.append("--enable-xml=yes")
    extra_conf.append("--enable-glesv2=yes")
    #extra_conf.append("--enable-drm=yes")
    extra_conf.append("--enable-egl=yes")
    extra_conf.append("--enable-ps=no") 
    extra_conf.append("--enable-pdf=no")
    extra_conf.append("--enable-svg=no")
    extra_conf.append("--enable-interpreter=no")
    extra_conf.append("--disable-gtk-doc")
    extra_conf.append("--disable-gtk-doc-html")
    extra_conf.append("--host=" + cc_host)
    extra_conf.append('pixman_CFLAGS=-I' + ops.path_join(iopc.getSdkPath(), 'usr/include/libpixman'))
    extra_conf.append('pixman_LIBS=-L' + ops.path_join(iopc.getSdkPath(), 'lib') + ' -lpixman-1')
    extra_conf.append('png_REQUIRES=libpng')
    extra_conf.append('png_CFLAGS=-I' + ops.path_join(iopc.getSdkPath(), 'usr/include/libpng'))
    extra_conf.append('png_LIBS=-L' + ops.path_join(iopc.getSdkPath(), 'lib') + ' -lpng')
    extra_conf.append('glesv2_CFLAGS=-I' + ops.path_join(iopc.getSdkPath(), 'usr/include/mesa'))
    extra_conf.append('glesv2_LIBS=-L' + ops.path_join(iopc.getSdkPath(), 'lib') + ' -lGLESv2')
    #extra_conf.append('drm_CFLAGS=-I' + ops.path_join(iopc.getSdkPath(), 'usr/include/libdrm'))
    #extra_conf.append('drm_LIBS=-L' + ops.path_join(iopc.getSdkPath(), 'lib') + ' -ldrm')
    #extra_conf.append('egl_CFLAGS=-I' + ops.path_join(iopc.getSdkPath(), 'usr/include/mesa -I' + ops.path_join(iopc.getSdkPath(),'usr/include/libudev')) + ' -DMESA_EGL_NO_X11_HEADERS')
    extra_conf.append('egl_CFLAGS=-I' + ops.path_join(iopc.getSdkPath(), 'usr/include/mesa ') + ' -DMESA_EGL_NO_X11_HEADERS')
    extra_conf.append('egl_LIBS=-L' + ops.path_join(iopc.getSdkPath(), 'lib') + ' -lEGL -lgbm -ldrm -lexpat -lwayland-client -lglapi -lffi -lwayland-server')
    print extra_conf
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

def MAIN_CLEAN_BUILD(args):
    set_global(args)

    return False

def MAIN(args):
    set_global(args)

