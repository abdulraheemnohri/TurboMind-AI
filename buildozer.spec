# (str) Title of your application
 title = TurboMind AI
 
 # (str) Package name
 package.name = turbomindai
 
 # (str) Package domain (needed for android/ios packaging)
 package.domain = com.abdulraheemnohri
 
 # (str) Source code where the main.py live
 source.dir = .
 
 # (list) Source files to include (let empty to include all the files)
 source.include_exts = py,png,jpg,kv,atlas,ttf,otf,woff,woff2
 
 # (list) List of inclusions using pattern matching
 #source.include_patterns = assets/*,images/*.png
 
 # (list) Source files to exclude (let empty to not exclude anything)
 #source.exclude_exts = spec
 
 # (list) List of directory to exclude (let empty to not exclude anything)
 source.exclude_dirs = tests, __pycache__, .git, docs, venv
 
 # (list) List of exclusions using pattern matching
 #source.exclude_patterns = license,images/*/*.jpg
 
 # (str) Application versioning (method 1)
 version = 1.0.0
 
 # (str) Application versioning (method 2)
 # version.regex = __version__ = ['"](.*)['"]
 # version.filename = %(source.dir)s/main.py
 
 # (list) Application requirements
 requirements = python3,kivy>=2.1.0,kivymd>=1.1.1,numpy>=1.24.0,torch>=2.0.0,transformers>=4.30.0,psutil,scipy,sentencepiece
 
 # (str) Custom source folders for requirements
 #requirements.source = 
 
 # (list) Garden requirements
 #garden_requirements = 
 
 # (str) Presplash of the application
 #presplash.filename = %(source.dir)s/data/presplash.png
 
 # (str) Icon of the application
 #icon.filename = %(source.dir)s/data/icon.png
 
 # (str) Supported orientation (one of landscape, portrait or all)
 orientation = portrait
 
 # (list) List of service to declare
 #services = NAME:ENTRYPOINT_TO_PYTHON_FILE
 
 # (str) WM of the application
 #window_manager = ivuik
 
 # (str) Android logcat filters (optional)
 #android.logcat_filters = *:S python:D
 
 # (bool) Copy library instead of making a libs.zip
 #android.copy_libs = 1
 
 # (str) Android NDK version (default is 19b)
 #android.ndk = 19b
 
 # (int) Android API to use (default is 27)
 android.api = 30
 
 # (int) Minimum API required (default is 21)
 android.minapi = 21
 
 # (int) Android SDK version to use (default is 27)
 #android.sdk = 27
 
 # (str) Android NDK directory (if empty, it will be automatically downloaded.)
 #android.ndk_path = 
 
 # (str) Android SDK directory (if empty, it will be automatically downloaded.)
 #android.sdk_path = 
 
 # (str) python-for-android branch to use
 #p4a.branch = master
 
 # (str) OUYA Console category. Should be one of GAME or APP
 #ouya.category = GAME
 
 # (str) Filename of the Android application manifest
 #android.manifest = 
 
 # (str) Android additional libraries to copy into libs/armeabi
 #android.add_libs_armeabi = libs/android/*.so
 
 # (str) Android additional libraries to copy into libs/armeabi-v7a
 #android.add_libs_armeabi_v7a = libs/android/*.so
 
 # (str) Android additional libraries to copy into libs/arm64-v8a
 #android.add_libs_arm64_v8a = libs/android/*.so
 
 # (str) Android additional libraries to copy into libs/x86
 #android.add_libs_x86 = libs/android/*.so
 
 # (str) Android additional libraries to copy into libs/x86_64
 #android.add_libs_x86_64 = libs/android/*.so
 
 # (bool) Indicate whether the screen should stay on
 #android.wakelock = False
 
 # (list) Android application meta-data to set (key=value format)
 #android.meta_data = 
 
 # (list) Android library project to add (will be added in the
 # project.properties automatically.)
 #android.library_references = 
 
 # (str) Android logcat file (optional)
 #android.logcat_filename = 
 
 # (bool) Only build the needed architecture(s) for Android
 #android.arch = armeabi-v7a, arm64-v8a
 
 # (int) Android Studio project level
 #android.gradle_version = 
 
 # (str) Android logcat filters
 #android.logcat_filters = *:S python:D
 
 # (bool) Use --private data storage (True) or --dir public storage (False)
 #android.private_storage = True
 
 # (str) Android architecture to build (armeabi-v7a, arm64-v8a, x86, x86_64)
 android.arch = arm64-v8a,armeabi-v7a
 
 # (bool) Enable Android hardware acceleration
 android.enable_hardware_acceleration = True
 
 # (str) Android entry point, default is ok for Kivy-based app
 #android.entrypoint = org.kivy.android.PythonActivity
 
 # (list) List of Java .jar files to add to the libs so that pyjnius can access
 # their classes. Don't add jars that you do not need, since extra jars can slow
 # down the build process. All the jars added will be available in the
 # class path for pyjnius.
 #android.add_jars = foo.jar,bar.jar,path/to/more/*.jar
 
 # (list) List of Java files to add to the android project (can be java or a
 # directory containing the files)
 #android.add_src = 
 
 # (list) Android AAR archives to add (currently works only with sdl2_gradle
 # bootstrap)
 #android.add_aars = 
 
 # (list) Gradle dependencies to add (currently works only with sdl2_gradle
 # bootstrap)
 #android.gradle_dependencies = 
 
 # (str) python-for-android whitelist (About allowing modules to be imported)
 #android.p4a_whitelist = 
 
 # (bool) Use p4a whitelist
 #android.p4a_whitelist_enable = True
 
 # (str) Bootstraps for android builds
 #android.bootstrap = sdl2
 
 # (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
 #p4a.port = 
 
 # (str) The Android archiver to use (default is auto-detected based on the
 # host architecture)
 #android.archiver = 
 
 # (bool) Run the application in a custom Android Activity
 #android.custom_activity = True
 
 # (str) The name of the custom Android Activity class
 #android.custom_activity_class = 
 
 # (str) The path to the custom Android Activity source file
 #android.custom_activity_source = 
 
 # (bool) Whether to use the custom activity as the main activity
 #android.custom_activity_as_main = True
 
 # (str) The Android NDK version to use for the custom activity
 #android.custom_activity_ndk = 
 
 # (bool) Use Android Studio project to build the application
 #android.use_android_studio = False
