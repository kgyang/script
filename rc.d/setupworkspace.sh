
# This script is used to setup development environment for hobby project.
# The syntax of command shall follow format:
#     hb<cmd> [<subcmd>] <args>
# For each command, _hb<cmd>() shall be defined, and it must
# support <-h> option to print usage information.
# For each subcommand, _hb<cmd>_<subcommand>() shall be defined.
# Note: all command functions must be defined before
#       get_hb_command_functions() to ensure command entry
#       functions generation

REPO_NAME=''
GIT_REPO_SERVER=''
JIRA_SERVER=''
JIRA_USER=''
JIRA_PASSWORD=''

set_root_workspace()
{
    ROOT_HB_WORKSPACE=$HOME/RootGit

    [[ -d $ROOT_HB_WORKSPACE ]] && return

    if [[ -n "$MSYSTEM" ]]
    then
        _pool=/c/RootGit
        [[ -d /d ]] && _pool=/d/RootGit
        ROOT_HB_WORKSPACE=$_pool
    else
        echo "no root workspace found" >&2
        return 1
    fi
    mkdir -p $_pool
    [[ $_pool == $ROOT_HB_WORKSPACE ]] || ln -T -s $_pool $ROOT_HB_WORKSPACE
}

get_user_root_workspace()
{
    if [[ -z "$1" || "$1" == $LOGNAME ]]
    then
        echo $ROOT_HB_WORKSPACE
    elif [[ -d /home/$1/RootGit ]]
    then
        echo /home/$1/RootGit
    fi
}

# findout all repositories in workspace
set_workspace_repositories()
{
    [[ -n "$HB_WORKSPACE" ]] || return

    if [[ -d $HB_WORKSPACE/.git ]]
    then
        _repos="$HB_WORKSPACE"
    else
        for _d in $HB_WORKSPACE/*
        do
            [[ -d ${_d}/.git ]] && _repos+=" $_d"
        done
    fi

    for _d in $_repos
    do
        _repo=$(cd ${_d}; basename $(git config remote.origin.url) | tr [:lower:] [:upper:] | tr '.' '_';)
        eval "export HB_${_repo}_REPOSITORY=${_d}"
    done
}

enter_workspace()
{
    alias makews='hbws make'
    alias removews='hbws remove'
    alias lsws='hbws list'
    alias setws='hbws set'

    [[ -n "$HB_WORKSPACE" ]] && {
        if [[ $(basename $SHELL) == 'ksh' ]]
        then
            export PS1="$'\e'[0;33m"'${PWD}($(basename $HB_WORKSPACE))'"$'\e'[m
-> "
        else
            export PS1="\[\e[0;33m\]"'${PWD}($(basename $HB_WORKSPACE))'"\[\e[m\]
-> "
        fi
        alias cmhost='hbcm host'
        alias cmhb='hbcm hb'

        set_workspace_repositories

        HB_WORKSPACE_DIRS=$(find $HB_WORKSPACE -maxdepth 4 \
                          -type d ! -path '*.git*' ! -path '*obj*')

        cd $HB_WORKSPACE
    }
}

_is_help_option()
{
    [[ "$1" == "?" || "$1" == "-h" || "$1" == "--help" ]]
}

# command hbws: workspace operation
_hbws()
{
    printf "hbws\t\t-- workspace commands\n" >&2
    echo "Usage: hbws <$(get_hb_sub_commands _hbws | \
                          paste -d'|' -s -)>" >&2
}

_do_setws()
{
    [[ $# -eq 1 ]] || return 1
    _wsdir=$1
    [[ -d $_wsdir ]] || { echo "$1 not found" >&2; return 1; }
    HB_WORKSPACE=$_wsdir $SHELL
}

_hbws_set()
{
    _is_help_option $1 && {
        echo "hbws set [-u <user>] [<workspacename>]" >&2
printf "\nThe 'hbws set' sets Git based workspace and needed
environment. By default, it looks for the workspapces owned by
caller and displays a list for selection. If user is specified,
it looks for those of the user. If workspacename is specified,
it looks for the workspace.\n" >&2
        return
    }

    _user=$LOGNAME
    [[ "$1" == "-u" ]] && {
        [[ -n "$2" ]] || { _hbws_set -h; return; }
        _user=$2
        shift 2
    }

    _wsroot=$(get_user_root_workspace $_user)
    [[ -n "$_wsroot" ]] || { echo "user not found" >&2; return; }

    if [[ $# -gt 0 ]]
    then
        _do_setws $_wsroot/$1
    else
        _wslist=$(ls $_wsroot | awk '{for (i = 0; i < NF; i++) print $(i+1);}' | sed 's#/$##')
        if [[ -z "$_wslist" ]]
        then
            echo "no workspace found" >&2
        else
            _wsnum=`wc -l <<< "$_wslist"`
            if [[ $_wsnum -eq 1 ]]
            then
                _do_setws $_wsroot/$_wslist
            else
                _oldps=$PS3
                PS3="Select a workspace: "
                select _ws in $_wslist
                do
                    if [[ -z "$_ws" ]]
                    then
                        echo "canceled ..." >&2
                    else
                        _do_setws $_wsroot/$_ws
                    fi
                    break
                done
                PS3=$_oldps
            fi
        fi
    fi
}

_hbws_list()
{
    _user=$LOGNAME
    [[ -z "$1" ]] || {
        [[ "$1" == "-u" && -n "$2" ]] || {
            echo "hbsws list [-u <user>]" >&2
printf "\nThe 'hbws list' looks for the workspapces owned by
caller (by default) or specified user.\n" >&2
            return
        }
        _user=$2
    }

    _wsroot=$(get_user_root_workspace $_user)
    [[ -n "$_wsroot" ]] || {
        echo "no workspaces found for $_user" >&2
        return
    }

    _wslist=$(ls $_wsroot)
    [[ -n "$_wslist" ]] || {
        echo "no workspaces found for $_user" >&2
        return
    }

    for _ws in $_wslist
    do
        [[ -d $_wsroot/$_ws ]] && echo $_ws
    done
}

_clonerepo()
{
    _repo=$1
    _branch=$2
    [[ -d $_repo ]] && return 0
    (
    git clone $GIT_REPO_SERVER/$_repo || return 1
    cd $_repo
    git config remote.origin.push refs/heads/*:refs/for/*
    git config http.sslverify false
    [[ -n "$_branch" ]] && {
        git checkout -b $_branch origin/$_branch || return 1
        #git config remote.${_branch}.push refs/heads/${_branch}:refs/for/${_branch}
        #git config remote.${_branch}.fetch +refs/heads/*:refs/remotes/origin/*
        #git config branch.${_branch}.remote ${_branch}
        #git config branch.${_branch}.merge refs/heads/${_branch}
    }
    )
    return 0
}

_hbws_make()
{
    _usage="
hbws make [-b <build-tag>] [-B <branch>] <workspacename>
    <build-tag>: 1.0-190704, LATEST_BUILD 

The 'hbws make' creates workspace by cloning git
repositories from server. The workspace name shall
be specified uniquely.

-b <build-tag>:
    specifies the build tag where the workspace to go.
    if not specified, the workspace is up-to-date. 

-B <branch>:
    specifies the branch of repositories of the workspace.
"
    _tag=''
    _repo=$REPO_NAME
    _branch=''
    while true
    do
        case "$1" in
            -h | --help | -\?)
                printf "$_usage\n" >&2
                return 1
                ;;
            -b) _tag=$2; shift 2;;
            -B) _branch=$2; shift 2;;
             *) break ;;
        esac
    done

    _ws=$1
    [[ -n "$_ws" ]] || {
        printf "$_usage\n" >&2
        return 1
    }

    _wsdir=$ROOT_HB_WORKSPACE/$_ws
    [[ -f $_wsdir ]] && {
        echo "conflict with filename under workspace directory" >&2
        return 2
    }

    [[ -d $_wsdir ]] && {
        echo "workspace already exist" >&2
        return 2
    }

    _ret=1
    (
    mkdir -p $_wsdir && cd $_wsdir || return 1
    for _r in $_repo
    do
        _clonerepo $_r $_branch || return 1
    done

    if [[ -n "$_tag" ]]
    then
        _tags=$(cd hbproj; git tag | grep -i $_tag)
        [[ -n "$_tags" ]] || {
            echo "unknown build tag" >&2
            return 1
        }

        _stag=''
        if [[ `wc -l <<< "$_tags"` -eq 1 ]]
        then
            _stag=$_tags
        else
            _oldps=$PS3
            PS3="Select a build tag: "
            select _stag in $_tags
            do
                [[ -n "$_stag" ]] || echo "canceled ..." >&2
                break
            done
            PS3=$_oldps
        fi
        [[ -n "$_stag" ]] || return 1
        echo "$_stag is selected for workspace being created"

        for _r in $_repo
        do
            (cd $_r; git reset --hard $_stag) || return 1
        done
    fi
    ) && _ret=0

    if [[ $_ret -eq 0 ]]
    then
        echo "$_ws created successfully" >&2
    else
        [[ -z "$MSYSTEM" ]] && rm -rf $_wsdir
        echo "failed to create $_ws" >&2
    fi
    return $_ret
}

_hbws_remove()
{
    [[ $# -gt 0 ]] || {
        echo "hbws remove <workspacename>..." >&2
printf "\nThe 'hbws remove' removes workspaces specified.\n" >&2
        return 1
    }
    for _ws in $*
    do
        _wsdir=$ROOT_HB_WORKSPACE/$_ws
        if [[ "$HB_WORKSPACE" == $_wsdir ]] 
        then
            echo "removing current workspace is not allowed" >&2
        else
            if [[ -d $_wsdir ]]
            then
                set -x
                rm -rf $_wsdir
                set +x
                echo "$_ws removed" >&2
            else
                echo "$_ws not exist" >&2
            fi
        fi
    done
}

_readanswer()
{
    read answer

    if grep -iq "y" <<< $answer
    then
        return 0
    elif grep -iq "n" <<< $answer
    then
        return 1
    fi

    echo "Please enter 'y'(=yes) or 'n'(=no)"
    _readanswer "$@"
}

# command hbgit: git operations
_hbgit()
{
    printf "hbgit\t\t-- git command wrapper\n" >&2
    echo "Usage: hbgit <$(get_hb_sub_commands _hbgit |\
                           paste -d'|' -s -)>" >&2
}

_hbgit_clone()
{
    [[ -n "$HB_WORKSPACE" ]] || {
        echo "not in workspace" >&2
        return 1
    }
    [[ $# -eq 0 ]] || [[ "$1" == "-B" && $# -lt 3 ]] || _is_help_option $1 && {
        echo "Usage: hbgit clone [-B <branch>] <repo>..." >&2
        printf "\t-B <branch>: specifies the branch of repositories\n" >&2
        printf "\nThe 'hbgit clone' clones repositories specified
in current workspace. If the repository specified already exists,
it skip the clone.\n" >&2
        return 2
    }

    (
        _branch=''
        [[ "$1" == "-B" ]] && {
            _branch=$2
            shift 2
        }
        cd $HB_WORKSPACE
        [[ ! -d .git ]] || {
            echo "could not clone in another repo" >&2
            return 3
        }

        for _repo in $*
        do
            _clonerepo $_repo $_branch || break
        done
    )

    set_workspace_repositories
}

_git_cppcheck()
{
    _cppchecktool=$HOME/script/git/git-cppcheck
    if [[ -f $_cppchecktool ]]
    then
        echo "git-cppcheck $*"
        $_cppchecktool $* || {
            echo "need to fix cppcheck warnings/errors" >&2
            return 1
        }
    fi
    return 0
}

_check_ascii_characters()
{
    _warning_flag=0
    _rootdir=$(git rev-parse --show-toplevel 2>/dev/null)
    for _file in $(git --no-pager diff --name-only --diff-filter=AMT HEAD)
    do
        if grep -q "^text/.*;" <<< $(file -ib $_rootdir/$_file)
        then
            #if grep -n -C 1 -P '[\x00-\x08\x0B-\x1F\x80-\xFF]' $_rootdir/$_file
            _lines=$(awk '/[^[:print:]\t]/{print NR":"$0}' $_rootdir/$_file)
            [[ -n "$_lines" ]] && {
                echo "$_file has non-printable ASCII characters in following lines:"
                echo "$_lines"
                _warning_flag=1
            }
        fi
    done
    return $_warning_flag
}

_in_master_branch()
{
    [[ "$(git rev-parse --abbrev-ref HEAD)" == "master" ]] || {
        echo "not in master branch" >&2
        return 1
    }
    return 0
}

_precommit()
{
    #_in_master_branch || return 1

    _git_cppcheck || return 1

    _root=$(git rev-parse --show-toplevel 2>/dev/null)
    [[ -n "$_root" ]] || { echo "not in git repository" >&2; return 1; }
    cd $_root
    _unstaged=$(git ls-files --others --exclude-standard)

    if [[ -n "$_unstaged" ]]
    then
        echo "$_unstaged"
        printf "The above files not staged. Include them? (y/n) "
        if _readanswer
        then
            git add $_unstaged || return 1
        fi
    fi
    cd - > /dev/null

    _check_ascii_characters
}

_hbgit_commit()
{
    [[ "$1" == "-m" ]] || {
        echo "Usage: hbgit commit -m <msg>" >&2
printf "\nThe 'hbgit commit' wraps 'git commit'.
Firstly, it checks if there're multiple commits, then it runs
cppcheck. If no error found, it runs 'git commit'.\n" >&2
        return 1
    }
    _msg="$(echo "$@" | sed "s/.*-m //")"

    _headmsg=$(git --no-pager log --format=%B -n 1 HEAD | head -1)
    [[ "${_headmsg}" == "${_msg}" ]] && {
        echo "You have committed already. Use 'hbgit add2commit'." >&2
        return 1
    }

    _precommit || return 1

    git commit -a -m "$_msg"
}

_hbgit_commitauto()
{
    [[ -z "$1" ]] || _is_help_option $1 && {
        echo "Usage: hbgit commitauto <issue>" >&2
printf "\nThe 'hbgit commitauto' will try to get the JIRA summary
field of a provided issue and use it as your commit message.
In addition, it will check if the issue assignee is caller and if
is in 'In Progress' status.
The complete text of the constructed 'hbgit commit' command
will be displayed. You type 'y' to run it or type 'n' for further
editing.\n" >&2
        return 1
    }

    _issue=$1
    grep -q 'HB-[[:digit:]]\+$' <<< $_issue || {
        echo "invalid issue $_issue: should be HB-<number>" >&2
        return 1
    }

    _json=$(curl -u $JIRA_USER:$JIRA_PASSWORD -X GET -H "Content-Type: application/json" \
            $JIRA_SERVER/rest/api/2/issue/$_issue 2>/dev/null)
    [[ -n "$_json" ]] || {
        echo "issue $_issue not found" >&2
        return 1
    }

    _python=python
    [[ -n "$MSYSTEM" ]] && _python=python.exe

    _title=$($_python -c 'import sys, json; print(json.load(sys.stdin)["fields"]["summary"])' <<< "$_json")
    [[ -n "$_title" ]] || {
        echo "issue $_issue title not found" >&2
        return 1
    }

    [[ "$_title" == "${_title## }" ]] || {
        echo "$_issue "\""$_title"\"" begins with white space" >&2
        return 1
    }

    [[ "$_title" == "${_title%% }" ]] || {
        echo "$_issue "\""$_title"\"" ends with white space" >&2
        return 1
    }

    grep -q '[^[:print:]]' <<< "$_title" && {
        echo "$_issue "\""$_title"\"" contains non-printable characters" >&2
        return 1
    }

    grep -q '  ' <<< "$_title" && {
        echo "$_issue "\""$_title"\"" contains continuous white space" >&2
        return 1
    }

    _assignee=$($_python -c 'import sys, json; print(json.load(sys.stdin)["fields"]["assignee"])' <<< "$_json")
    [[ "$_assignee" == "None" ]] && {
        echo "$_issue is not assigned" >&2
        return 1
    }

    _email=$($_python -c 'import sys, json; print(json.load(sys.stdin)["fields"]["assignee"]["emailAddress"])' <<< "$_json")
    _gitemail=$(git config user.email)
    [[ "$_email" == "$_gitemail" ]] || {
        echo "assignee.email($_email) conflicts to git user.email($_gitemail)" >&2
        return 1
    }

    _status=$($_python -c 'import sys, json; print(json.load(sys.stdin)["fields"]["status"]["name"])' <<< "$_json")
    [[ "$_status" == 'In Progress' ]] || {
        echo "$_issue status($_status) is not 'In Progress'" >&2
        return 1
    }

    _msg="$_issue: $_title"
    printf '\n\thbgit commit -m \"%s\"\n' "$_msg"
    printf '\nWould you like to execute this command? (y/n): '
    _readanswer || return 0
    _hbgit_commit -m "$_msg"
}

_hbgit_add2commit()
{
    _precommit || return 1
    _changes=$(git --no-pager diff --name-only HEAD 2>/dev/null)
    if [[ -n "$_changes" ]]
    then
        _msg=$(git --no-pager log -n 1 --pretty=format:%B HEAD)
        if [[ -z "$1" ]]
        then
            git add -u
            git commit --amend -m "$_msg"
        else
            git commit --amend -m "$_msg" -- "$@"
        fi
    else
        echo "nothing to commit" >&2
    fi
}

_hbgit_abandoncommit()
{
    git --no-pager log -n 1 HEAD
    printf "!!! Abandon above commit? (The changes in commit will
retain in your workspace) (y/n) "
    _readanswer || return 0
    git reset --soft HEAD^
}

_hbgit_pullrebase()
{
    if [[ $PWD == "$HB_WORKSPACE" && ! -d "$HB_WORKSPACE"/.git ]]
    then
        for _d in *
        do
            [ -d $_d/.git ] && ( set -x; cd $_d; git pull --rebase $*; )
        done
    else
        git pull --rebase $*
    fi
}

_hbgit_push()
{
    #_in_master_branch || return 1

    #[[ "$(git rev-parse origin/master)" == "$(git rev-parse HEAD^)" ]] || {
        #echo "You have multiple commits, push is not allowed" >&2
        #return 1
    #}

    git push $*
}

# command hbcd: change directory under workspace
_hbcd()
{
    _is_help_option $1 && {
        printf "hbcd\t\t-- change directory in workspace smartly\n" >&2
        echo "Usage: hbcd [<dir>]" >&2
printf "\nThe 'hbcd' changes directory in workspace smartly.
It searches direcotries under workspace that matches your
input. The input could be regular expression or normal string.
The search depth is up to 4.
If multiple results found, selection menu will be prompted
for selection.
Examples:
    hbcd driver 
        go to directory contains driver
\n" >&2
        return
    }

    [[ $# -eq 0 ]] && { cd $HB_WORKSPACE; return; }

    [[ -d $1 ]] && { cd $1; return; }

    # if input is regex
    if grep -q '\$\|\[\|\*\|?\|\+\||\|\.' <<< "$1"
    then
        _matches=$(grep -ie "$HB_WORKSPACE.*$1" <<< \
                   $HB_WORKSPACE_DIRS)
    else
        _matches=$(grep -ie "$HB_WORKSPACE.*/$1$" <<< \
                   $HB_WORKSPACE_DIRS)
        _matches+=" "$(grep -ie "$HB_WORKSPACE.*/$1/" <<< \
                   $HB_WORKSPACE_DIRS)
        _matches+=" "$(grep -ie "$HB_WORKSPACE.*$1" <<< \
                   $HB_WORKSPACE_DIRS \
                   | grep -vie "/$1$" | grep -vie "/$1/")
        _matches=$(sed 's/^ \+//; s/ \+$//' <<< "$_matches")
    fi
    [[ -n "$_matches" ]] || {
        echo "no directory found" >&2
        return 1
    }

    if [[ $(wc -l <<< "$_matches") -eq 1 ]]
    then
        cd $_matches
    else
        _oldps=$PS3
        PS3="Select a directory to go: "
        select _dir in $_matches
        do
            if [[ -n "$_dir" ]]
            then
                cd $_dir
            else
                echo "canceled ..." >&2
            fi
            break
        done
        PS3=$_oldps
    fi
}

# following codes must be placed in the end to generate command entry functions and help command function
get_hb_command_functions()
{
    # echo "_hbws _hbcd _hbcm _hbgit ..."
    if [[ $(basename $SHELL) == 'ksh' ]]
    then
        typeset +f | sed -n 's/^\(_hb[^_]*\)()$/\1/p'
    else
        declare -F | awk '{print $3}' | sed -n 's/^\(_hb[^_]*\)$/\1/p'
    fi
}

get_hb_sub_commands()
{
    _cmd=$1
    if [[ $(basename $SHELL) == 'ksh' ]]
    then
        typeset +f | sed -n "s/^${1}_\(.*\)()$/\1/p"
    else
        declare -F | awk '{print $3}' | sed -n "s/^${1}_\(.*\)/\1/p"
    fi
}

hbhelp()
{
    for _cmd in $(get_hb_command_functions)
    do
        $_cmd -h 2>&1 | head -1
    done
}

generate_hb_command_entry_functions()
{
    for _cmd in $(get_hb_command_functions)
    do
        # remove '_' from command function name,
        # use it as command entry function name
        eval "${_cmd:1}()
{
    _subcmd=\$1
    _subfunc=${_cmd}_\${_subcmd}
    if type \${_subfunc} 2> /dev/null | grep -q 'is a function'
    then
        shift
        \${_subfunc} \$*
    else
        ${_cmd} \$*
    fi
}
"
    done
}

# here to run
generate_hb_command_entry_functions
set_root_workspace
enter_workspace
