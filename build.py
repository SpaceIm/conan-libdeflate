from cpt.packager import ConanMultiPackager

if __name__ == "__main__":
    recipe_name = "libdeflate"
    recipe_version = "1.8"
    username = "SpaceIm"
    channel = "testing"
    reference = "{}/{}@{}/{}".format(recipe_name, recipe_version, username, channel)

    shared_option_name = "{}:shared".format(recipe_name)
    pure_c = True

    builder = ConanMultiPackager(username=username, channel=channel,
                                 build_policy="missing", skip_check_credentials=True)
    builder.add_common_builds(shared_option_name=shared_option_name, pure_c=pure_c, dll_with_static_runtime=True,
                              reference=reference, build_all_options_values=None)
    builder.run()
