#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import re
import time

from distutils.command.build import build
from setuptools import setup

class my_build(build):
    user_options = build.user_options

    description = "build everything needed to install"

    def gen_rpm_spec(self):
        f1 = open('libvirt-sandbox-image.spec.in', 'r')
        f2 = open('libvirt-sandbox-image.spec', 'w')
        for line in f1:
            f2.write(line
                     .replace('@PY_VERSION@', self.distribution.get_version()))
        f1.close()
        f2.close()

    def gen_authors(self):
        f = os.popen("git log --pretty=format:'%aN <%aE>'")
        authors = []
        for line in f:
            authors.append("   " + line.strip())

        authors.sort(key=str.lower)

        f1 = open('AUTHORS.in', 'r')
        f2 = open('AUTHORS', 'w')
        for line in f1:
            f2.write(line.replace('@AUTHORS@', "\n".join(set(authors))))
        f1.close()
        f2.close()

    def gen_man_pages(self):
        for path in glob.glob("man/*.pod"):
            base = os.path.basename(path)
            appname = os.path.splitext(base)[0]
            newpath = os.path.join(os.path.dirname(path),
                                   appname + ".1")

            print("Generating %s" % newpath)
            ret = os.system('pod2man '
                            '--center "Virtualization Support" '
                            '--release %s --name %s '
                            '< %s > %s' % (self.distribution.get_version(),
                                           appname.upper(),
                                           path, newpath))
            if ret != 0:
                raise RuntimeError("Generating '%s' failed." % newpath)

        if os.system("grep -IRq 'Hey!' man/") == 0:
            raise RuntimeError("man pages have errors in them! "
                               "(grep for 'Hey!')")

    def gen_changelog(self):
        f1 = os.popen("git log '--pretty=format:%H:%ct %an  <%ae>%n%n%s%n%b%n'")
        f2 = open("ChangeLog", 'w')

        for line in f1:
            m = re.match(r'([a-f0-9]+):(\d+)\s(.*)', line)
            if m:
                t = time.gmtime(int(m.group(2)))
                f2.write("%04d-%02d-%02d %s\n" % (t.tm_year, t.tm_mon, t.tm_mday, m.group(3)))
            else:
                if re.match(r'Signed-off-by', line):
                    continue
                f2.write("    " + line.strip() + "\n")

        f1.close()
        f2.close()


    def run(self):
        if not os.path.exists("build"):
            os.mkdir("build")

        if os.path.exists(".git"):
            try:
                self.gen_rpm_spec()
                self.gen_authors()
                self.gen_changelog()
                self.gen_man_pages()
                build.run(self)

            except:
                files = ["libvirt-sandbox-image.spec",
                         "AUTHORS",
                         "ChangeLog"]
                for f in files:
                    if os.path.exists(f):
                        os.unlink(f)
                raise
        else:
            build.run(self)

setup(
    name="libvirt-sandbox-image",
    version="1.0",
    description="A program for running container or VM images in sandboxes",
    long_description=""
    "This package provides a program that is able to run container or VM"
    "images in the sandbox environment provided by libvirt-sandbox."
    "Currently docker and virt-builder images are supported.",
    author="Libvirt Maintaniers",
    author_email="libvir-list@redhat.com",
    license="LGPLv2+",
    url="https://libvirt.org/",
    scripts=([
        "scripts/virt-sandbox-image",
        ]),
    packages=[
        "libvirt_sandbox_image",
        "libvirt_sandbox_image/sources"
    ],
    data_files=[
        ("share/man/man1", [
            "man/virt-sandbox-image.1",
            "man/virt-sandbox-image-prepare.1",
            "man/virt-sandbox-image-run.1",
            "man/virt-sandbox-image-list.1",
            "man/virt-sandbox-image-purge.1",
        ]),
    ],
    install_requires=[],
    cmdclass={
        'build': my_build,
    },
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
