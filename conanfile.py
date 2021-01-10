from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
import os


class LibdeflateConan(ConanFile):
    name = "libdeflate"
    description = "Heavily optimized library for DEFLATE/zlib/gzip compression and decompression."
    license = "MIT"
    topics = ("conan", "libdeflate", "compression", "decompression", "deflate", "gzip")
    homepage = "https://github.com/ebiggers/libdeflate"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        if self.settings.compiler == "Visual Studio":
            makefile_msc_file = os.path.join(self._source_subfolder, "Makefile.msc")
            tools.replace_in_file(makefile_msc_file, "CFLAGS = /MD /O2 -I.", "CFLAGS = /nologo $(CFLAGS) -I.")
            tools.replace_in_file(makefile_msc_file, "LDFLAGS =", "")
            with tools.chdir(self._source_subfolder):
                with tools.vcvars(self.settings):
                    with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                        target = "libdeflate.dll" if self.options.shared else "libdeflatestatic.lib"
                        self.run("nmake /f Makefile.msc {}".format(target))
        else:
            with tools.chdir(self._source_subfolder):
                with tools.environment_append(AutoToolsBuildEnvironment(self).vars):
                    self.run("make -f Makefile")

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            self.copy("libdeflate.h", dst="include", src=self._source_subfolder)
            if self.options.shared:
                self.copy("libdeflate.lib", dst="lib", src=self._source_subfolder)
                self.copy("libdeflate.dll", dst="bin", src=self._source_subfolder)
            else:
                self.copy("libdeflatestatic.lib", dst="lib", src=self._source_subfolder)
        else:
            with tools.chdir(self._source_subfolder):
                with tools.environment_append(AutoToolsBuildEnvironment(self).vars):
                    self.run("make -f Makefile install")

    def package_info(self):
        prefix = "lib" if self.settings.compiler == "Visual Studio" else ""
        suffix = "static" if self.settings.os == "Windows" and not self.options.shared else ""
        self.cpp_info.libs = ["{0}deflate{1}".format(prefix, suffix)]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines = ["LIBDEFLATE_DLL"]
