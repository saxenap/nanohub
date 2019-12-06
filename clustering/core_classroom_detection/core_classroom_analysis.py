from pprint import pprint


def core_classroom_analysis(inparams):

    pprint('hi')
    return

    toolstart_df = pd.read_feather(os.path.join(inparam['db_data_dir'], 'toolstart.feather'))
    toolstart_df['tool'] = toolstart_df['tool'].apply(lambda x: x.lower())
    display(toolstart_df)

    jos_tool_version = pd.read_feather(os.path.join(inparam['db_data_dir'], 'jos_tool_version.feather'))
    display(jos_tool_version)

    jos_users = pd.read_feather(os.path.join(inparam['db_data_dir'], 'jos_users.feather'))
    display(jos_users)
