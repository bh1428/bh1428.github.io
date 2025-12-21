+++
date = "2025-12-11T22:33:16+01:00"
draft = false
title = "Git under the hood"
tags = ["git", "dvcs"]
+++
You probably know [Git][git] and might be aware of the hidden `.git` folder where the actual repository is stored. Have you ever looked under the hood? Ever felt the need to know how Git does this magical thing with [`clone`][git_clone], [`commit`][git_commit], [`branch`][git_branch], etc.? What happens in the `.git` folder when you add a file? This article explores, for some of the standard operations, what really happens in the `.git` folder when a command is issued. Let's see how deep the rabbit hole goes!

<!--more-->
First of all, as a reminder: [Git][wikipedia_git] and [GitHub][wikipedia_github] are not the same. According to [Wikipedia][wikipedia]: "[Git][wikipedia_git] is a _distributed version control software system_ originally created by [Linus Torvalds][wikipedia_linus_torvalds] for version control in the development of the Linux kernel. [GitHub][wikipedia_github] is a _proprietary developer platform_ that allows developers to create, store, manage, and share their code." The only connection between the two is that [GitHub][wikipedia_github] uses [Git][wikipedia_git]. The same goes for sites like [GitLab][gitlab], [Bitbucket][bitbucket], [SourceForge][sourceforge], [AWS CodeCommit](https://aws.amazon.com/codecommit/) and even [Gitea][gitea]. Although they all use [Git][wikipedia_git] as repository, they are based on and add layers upon [Git][wikipedia_git] but are not the same.

For this article you should have a basic knowledge of Git: you should know terminology like repository, commit, branch, HEAD, index, etc. In case you need a refresher, search for "basic git tutorial" in your favorite search engine (or ask an LLM). Examples in this article are on Linux ([WSL][windows_wsl] with [Ubuntu 24.04.3 LTS][ubuntu]) using Git version 2.43.0.

## Table of Contents <!-- omit in toc -->

- [Creating a new repository](#creating-a-new-repository)
- [Adding a file](#adding-a-file)
- [The first commit](#the-first-commit)
- [Changing a file](#changing-a-file)
- [Inspiration](#inspiration)

## Creating a new repository

There are two types of Git repositories: **bare** and **non-bare**. A [bare][git_on_a_server] repository is normally used on a server (to be shared between developers) and does not contain a working directory. A non-bare repository is what you use for working on a project. Non-bare repositories contain a hidden `.git` folder which is equivalent to the content of a bare repository. Let's explore...

Create a (non-bare) repository with the [`git init`][git_init] command. Repositories are created from the [template directory][git_template_directory], the default default template directory is: `/usr/share/git-core/templates`:

```text
user@host:~$ git init non-bare
Initialized empty Git repository in /home/user/non-bare/.git/
```

Although [hooks][git_hooks], local [exclude](git_exclude) and the description file are very useful, they are not essential and for the sake of this article only add noise. Let's remove them and see what is in our `.git` folder:

```text
user@host:~$ cd ~/non-bare/
user@host:~/non-bare$ rm .git/hooks/* .git/info/exclude .git/description
user@host:~/non-bare$ find . -ls
    86787      4 drwxr-xr-x   3 user     user         4096 Dec 11 22:09 .
    86788      4 drwxr-xr-x   7 user     user         4096 Dec 11 22:10 ./.git
    86819      4 -rw-r--r--   1 user     user           92 Dec 11 22:09 ./.git/config
    86814      4 drwxr-xr-x   4 user     user         4096 Dec 11 22:09 ./.git/refs
    86816      4 drwxr-xr-x   2 user     user         4096 Dec 11 22:09 ./.git/refs/tags
    86815      4 drwxr-xr-x   2 user     user         4096 Dec 11 22:09 ./.git/refs/heads
    86791      4 drwxr-xr-x   2 user     user         4096 Dec 11 22:10 ./.git/hooks
    86817      4 -rw-r--r--   1 user     user           21 Dec 11 22:09 ./.git/HEAD
    86811      4 drwxr-xr-x   2 user     user         4096 Dec 11 22:10 ./.git/info
    86813      4 drwxr-xr-x   2 user     user         4096 Dec 11 22:09 ./.git/branches
    86818      4 drwxr-xr-x   4 user     user         4096 Dec 11 22:09 ./.git/objects
    86820      4 drwxr-xr-x   2 user     user         4096 Dec 11 22:09 ./.git/objects/pack
    86821      4 drwxr-xr-x   2 user     user         4096 Dec 11 22:09 ./.git/objects/info
```

Let's dump the content of the files (using [dump_file_tree.py]({{< param "github.benhattem_nl" >}}blob/main/content/posts/202512/git_under_the_hood/dump_file_tree.py)):

```text
user@host:~/non-bare$ ../dump_file_tree.py
>>> /home/user/non-bare/.git/config (UTF-8: 92 bytes)
1: [core]
2:     repositoryformatversion = 0
3:     filemode = true
4:     bare = false
5:     logallrefupdates = true
<<< /home/user/non-bare/.git/config

>>> /home/user/non-bare/.git/HEAD (UTF-8: 21 bytes)
1: ref: refs/heads/main
<<< /home/user/non-bare/.git/HEAD
```

That's all: the essence of an empty Git repository is just two files... isn't it beautiful?

A bare repository is created by using the [`--bare`][git_init_bare] (e.g. `git init --bare bare.git`). By convention, bare repositories are in folders with a name ending in `.git`. If you initialize a bare repository, you will get exactly the same result as shown above with one difference: everything is now stored in the main folder (`bare.git`) and there is no `bare.git/.git` folder. Go ahead, try it out.

## Adding a file

We now have an empty repository without any commits. Git tells you this when you ask with [`git status`][git_status]:

```text
user@host:~/non-bare$ git status
On branch main

No commits yet

nothing to commit (create/copy files and use "git add" to track)
```

As mentioned in the [YouTube - LearnThatStack - Git Will Finally Make Sense After This][learnthatstack_git_makes_sense] video: `HEAD` is a pointer (reference) to the `main` branch. At the moment we do not have a `main` branch, because we have nothing committed (there is nothing to point to). Let's add a file without committing (yet):

```text
user@host:~/non-bare$ echo "content file 1" > file1.txt
user@host:~/non-bare$ git add file1.txt
user@host:~/non-bare$ git status
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   file1.txt
```

Has anything changed in the `.git` folder? Let's see:

```text
user@host:~/non-bare$ ../dump_file_tree.py
>>> /home/user/non-bare/file1.txt (UTF-8: 15 bytes)
1: content file 1
<<< /home/user/non-bare/file1.txt

>>> /home/user/non-bare/.git/index (BINARY: 104 bytes)
00: 44 49 52 43 00 00 00 02 00 00 00 01 69 3b 34 2e 12 6e f5 14 69 3b 34 2e 12  DIRC........i;4..n..i;4..
19: 6e f5 14 00 00 08 50 00 00 22 03 00 00 81 a4 00 00 03 e8 00 00 03 e8 00 00  n.....P.."...............
32: 00 0f 17 25 18 7f 20 09 2d 75 cc ef 9e 55 75 23 1f bf 3a 8f ab 08 00 09 66  ...%.. .-u...Uu#..:.....f
4b: 69 6c 65 31 2e 74 78 74 00 1d 65 7c a0 21 5e ad 79 56 4e e6 5e 81 12 9e c3  ile1.txt..e|.!^.yVN.^....
64: ee de 4c 3d                                                                 ..L=
<<< /home/user/non-bare/.git/index

>>> /home/user/non-bare/.git/config (UTF-8: 92 bytes)
1: [core]
2:     repositoryformatversion = 0
3:     filemode = true
4:     bare = false
5:     logallrefupdates = true
<<< /home/user/non-bare/.git/config

>>> /home/user/non-bare/.git/HEAD (UTF-8: 21 bytes)
1: ref: refs/heads/main
<<< /home/user/non-bare/.git/HEAD

>>> /home/user/non-bare/.git/objects/17/25187f20092d75ccef9e5575231fbf3a8fab08 (BINARY: 31 bytes)
00: 78 01 4b ca c9 4f 52 30 34 65 48 ce cf 2b 49 cd 2b 51 48 cb cc 49 55 30 e4  x.K..OR04eH..+I.+QH..IU0.
19: 02 00 5a 9f 07 3c                                                           ..Z..<
<<< /home/user/non-bare/.git/objects/17/25187f20092d75ccef9e5575231fbf3a8fab08
```

Notice these changes:

- The file `/home/user/non-bare/file1.txt` has (obviously) been added.
- The _index_ (`.git/index`) is created and in its content we see the `file1.txt` filename.
- A file `.git/objects/17/25187f20092d75ccef9e5575231fbf3a8fab08` is created.

Let's start from the beginning: files in Git are stored as [blob][git_blob_object]'s with a name based on a SHA-1. A SHA-1 hash for an object is calculated from a header and the file content itself (see also [Pro Git Book - Object Storage][pro_git_book_object_storage]). The header for a binary blob has this form: `blob #{content.bytesize}\0`. Knowing this, we can calculate the SHA-1 ourselves (using Python):

```bash
python3 <<EOF
import pathlib
import hashlib
f = pathlib.Path("file1.txt")
f_size = f.stat().st_size
header = f"blob {f_size}".encode("utf-8") + b'\0'
print(hashlib.sha1(header + f.read_bytes()).hexdigest())
EOF
```

We get `1725187f20092d75ccef9e5575231fbf3a8fab08` as output which corresponds nicely with the new object: `.git/objects/17/25187f20092d75ccef9e5575231fbf3a8fab08` (the first two characters (`17`) are used as folder name). In other words: as a result of the `git add` command an object is created to store our new file. However, we trust no one, is it really our file?

```text
user@host:~/non-bare$ file .git/objects/17/25187f20092d75ccef9e5575231fbf3a8fab08
.git/objects/17/25187f20092d75ccef9e5575231fbf3a8fab08: zlib compressed data
```

It appears to be _zlib compressed_, let's have a look:

```bash
python3 <<EOF
import pathlib
import zlib
f = pathlib.Path(".git/objects/17/25187f20092d75ccef9e5575231fbf3a8fab08")
print(zlib.decompress(f.read_bytes()))
EOF
```

This prints `b'blob 15\x00content file 1\n'`, so... yes, it is our file (with an added header). As an alternative, you can  use the [`git show`][git_show] command as well:

```text
user@host:~/non-bare$ git show 1725187f20092d75ccef9e5575231fbf3a8fab08
content file 1
```

We now have only one missing piece: the [index][git_index] (`.git/index`) was created as well. How is it linked to our object? How does Git known that our tracked object is represented by the `.git/objects/17/25187f20092d75ccef9e5575231fbf3a8fab08` blob? In Git, everything is linked using hashes. If you look carefully, you can find the SHA-1 (together with the filename) in the `.git/index` as well:

```text
>>> /home/user/non-bare/.git/index (BINARY: 104 bytes)
00: .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. ..  DIRC........i;4..n..i;4..
19: .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. ..  n.....P.."...............
32: .. .. 17 25 18 7f 20 09 2d 75 cc ef 9e 55 75 23 1f bf 3a 8f ab 08 .. .. 66  ...%.. .-u...Uu#..:.....f
4b: 69 6c 65 31 2e 74 78 74 .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. ..  ile1.txt..e|.!^.yVN.^....
64: .. .. .. ..                                                                 ..L=
<<< /home/user/non-bare/.git/index
```

The real answer is: `.git/index` contains an encoded structure (see [Git index format][git_index_format] for more details) for each file. This structure contains the SHA-1 hash of the object but also the filename and information like modification time, size, owner, authorization, etc. If you want to see this using standard commands you can use the [`git ls-files --stage`][git_ls_files_stage] command as well:

```text
user@host:~/non-bare$ git ls-files --stage
100644 1725187f20092d75ccef9e5575231fbf3a8fab08 0       file1.txt
```

## The first commit

Let's commit our new file and see what happens:

```text
user@host:~/non-bare$ git commit -m "first commit"
[main (root-commit) 21590f7] first commit
 1 file changed, 1 insertion(+)
 create mode 100644 file1.txt
user@host:~/non-bare$ git status
On branch main
nothing to commit, working tree clean
```

What has changed?

```text
>>> /home/user/non-bare/file1.txt (UTF-8: 15 bytes)
1: content file 1
<<< /home/user/non-bare/file1.txt

>>> /home/user/non-bare/.git/index (BINARY: 137 bytes)
00: 44 49 52 43 00 00 00 02 00 00 00 01 69 3b 34 2e 12 6e f5 14 69 3b 34 2e 12  DIRC........i;4..n..i;4..
19: 6e f5 14 00 00 08 50 00 00 22 03 00 00 81 a4 00 00 03 e8 00 00 03 e8 00 00  n.....P.."...............
32: 00 0f 17 25 18 7f 20 09 2d 75 cc ef 9e 55 75 23 1f bf 3a 8f ab 08 00 09 66  ...%.. .-u...Uu#..:.....f
4b: 69 6c 65 31 2e 74 78 74 00 54 52 45 45 00 00 00 19 00 31 20 30 0a c3 6d ef  ile1.txt.TREE.....1 0..m.
64: c2 a7 e6 fa b6 1a f1 e1 f6 31 af 8b b5 cc a9 5e d1 3d 91 17 e7 44 80 0c b7  .........1.....^.=...D...
7d: 98 18 76 40 50 ca fc 13 e5 f2 cb dc                                         ..v@P.......
<<< /home/user/non-bare/.git/index

>>> /home/user/non-bare/.git/COMMIT_EDITMSG (UTF-8: 13 bytes)
1: first commit
<<< /home/user/non-bare/.git/COMMIT_EDITMSG

>>> /home/user/non-bare/.git/config (UTF-8: 92 bytes)
1: [core]
2:     repositoryformatversion = 0
3:     filemode = true
4:     bare = false
5:     logallrefupdates = true
<<< /home/user/non-bare/.git/config

>>> /home/user/non-bare/.git/HEAD (UTF-8: 21 bytes)
1: ref: refs/heads/main
<<< /home/user/non-bare/.git/HEAD

>>> /home/user/non-bare/.git/refs/heads/main (UTF-8: 41 bytes)
1: 21590f740c9cb696bf7b207fe9c8114be9283fc7
<<< /home/user/non-bare/.git/refs/heads/main

>>> /home/user/non-bare/.git/logs/HEAD (UTF-8: 164 bytes)
1: 0000000000000000000000000000000000000000 21590f740c9cb696bf7b207fe9c8114be9283fc7 Some User
   <some.user@example.org> 1765488030 +0100    commit (initial): first commit
<<< /home/user/non-bare/.git/logs/HEAD

>>> /home/user/non-bare/.git/logs/refs/heads/main (UTF-8: 164 bytes)
1: 0000000000000000000000000000000000000000 21590f740c9cb696bf7b207fe9c8114be9283fc7 Some User
   <some.user@example.org> 1765488030 +0100    commit (initial): first commit
<<< /home/user/non-bare/.git/logs/refs/heads/main

>>> /home/user/non-bare/.git/objects/c3/6defc2a7e6fab61af1e1f631af8bb5cca95ed1 (BINARY: 53 bytes)
00: 78 01 2b 29 4a 4d 55 30 36 67 30 34 30 30 33 31 51 48 cb cc 49 35 d4 2b a9  x.+)JMU06g040031QH..I5.+.
19: 28 61 10 57 95 a8 57 e0 d4 2d 3d f3 7e 5e 68 a9 b2 fc 7e ab fe d5 1c 00 26  (a.W..W..-=.~^h...~.....&
32: e2 0e 27                                                                    ..'
<<< /home/user/non-bare/.git/objects/c3/6defc2a7e6fab61af1e1f631af8bb5cca95ed1

>>> /home/user/non-bare/.git/objects/21/590f740c9cb696bf7b207fe9c8114be9283fc7 (BINARY: 129 bytes)
00: 78 01 9d 8d 41 0a c2 30 10 00 3d e7 15 7b 17 4a d6 98 34 05 91 fe 41 7c c0  x...A..0..=..{.J..4...A|.
19: 66 bb d1 82 21 92 a4 d0 e7 1b f4 07 de e6 32 33 9c 53 5a 1b e0 38 1d 5a 11  f...!.........23.SZ..8.Z.
32: 01 36 6e 91 c8 27 1a c5 45 0a 0e 29 a2 60 74 a6 83 0f c1 32 d3 64 65 41 45  .6n..'..E..).`t....2.deAE
4b: 5b 7b e6 02 b7 9c 04 ee 55 0a 5c 6a c7 61 eb 38 cb 4e e9 fd 92 21 97 c7 b5  [{......U.\j.a.8.N...!...
64: a7 9d 3d 7b af 8d 86 a3 46 ad 15 7f 97 ad 2b 7f c8 2a ae a5 36 f8 35 d4 07  ..={....F.....+..*..6.5..
7d: b6 89 3b f9                                                                 ..;.
<<< /home/user/non-bare/.git/objects/21/590f740c9cb696bf7b207fe9c8114be9283fc7

>>> /home/user/non-bare/.git/objects/17/25187f20092d75ccef9e5575231fbf3a8fab08 (BINARY: 31 bytes)
00: 78 01 4b ca c9 4f 52 30 34 65 48 ce cf 2b 49 cd 2b 51 48 cb cc 49 55 30 e4  x.K..OR04eH..+I.+QH..IU0.
19: 02 00 5a 9f 07 3c                                                           ..Z..<
<<< /home/user/non-bare/.git/objects/17/25187f20092d75ccef9e5575231fbf3a8fab08
```

The [`git log`][git_log] command shows:

```text
user@host:~/non-bare$ git log
commit 21590f740c9cb696bf7b207fe9c8114be9283fc7 (HEAD -> main)
Author: Some User <some.user@example.org>
Date:   Thu Dec 11 22:20:30 2025 +0100

    first commit
```

Summarized:

- The index `.git/index` is modified, a `TREE` is added.
- The commit message is stored in `.git/COMMIT_EDITMSG` (nice to know, but not that interesting).
- Logs are created: `.git/logs/HEAD` and `.git/logs/refs/heads/main`. This is used for [`git log`][git_log] and [`git reflog`][git_reflog], we will not explorer this further here.
- Two new objects are created: `.git/objects/c3/6defc2a7e6fab61af1e1f631af8bb5cca95ed1` and `.git/objects/21/590f740c9cb696bf7b207fe9c8114be9283fc7`.
- Our `main` branch is created in `.git/refs/heads/main` (and `HEAD` points to this branch: `refs/heads/main`)

As shown in the [`git status`][git_status] output, we now have a `main` branch and `HEAD` points to this `main` branch. The commit SHA-1 itself (`21590f740c9cb696bf7b207fe9c8114be9283fc7`) points to an object describing the commit content. To show this, we can use our Python script again but we may also use the standard [`git cat-file`][git_cat_file] command. First find out the type using the [`-t`][git_cat_file_t]:

```text
user@host:~/non-bare$ git cat-file -t 21590f740c9cb696bf7b207fe9c8114be9283fc7
commit
```

It's a [commit object][git_commit_object], we knew that already, but it's nice to get it confirmed. What does it contain? We can use the [`-p`][git_cat_file_p] option:

```text
user@host:~/non-bare$ git cat-file -p 21590f740c9cb696bf7b207fe9c8114be9283fc7
tree c36defc2a7e6fab61af1e1f631af8bb5cca95ed1
author Some User <some.user@example.org> 1765488030 +0100
committer Some User <some.user@example.org> 1765488030 +0100

first commit
```

It is linked to a [tree][git_tree_objects] which is again a Git object (`c36defc2a7e6fab61af1e1f631af8bb5cca95ed1`), let's have a look:

```text
user@host:~/non-bare$ git cat-file -p c36defc2a7e6fab61af1e1f631af8bb5cca95ed1
100644 blob 1725187f20092d75ccef9e5575231fbf3a8fab08    file1.txt
```

And there we have our file object `1725187...` again. So we go from `21590f740c9cb696bf7b207fe9c8114be9283fc7` (commit) to `c36defc2a7e6fab61af1e1f631af8bb5cca95ed1` (tree) to `1725187f20092d75ccef9e5575231fbf3a8fab08` as a file in that tree. Note: trees are stored at multiple levels: a subdirectory will be stored as a separate tree (not shown here).

## Changing a file

Finally, lets quickly change a file and see what happens during the commit:

```bash
echo "new content" > file1.txt
git add -A .
git commit -m "second commit"
```

`.git` content:

```text
>>> /home/user/non-bare/file1.txt (UTF-8: 12 bytes)
1: new content
<<< /home/user/non-bare/file1.txt

>>> /home/user/non-bare/.git/index (BINARY: 137 bytes)
00: 44 49 52 43 00 00 00 02 00 00 00 01 69 3b 37 52 2b 01 98 a8 69 3b 37 52 2b  DIRC........i;7R+...i;7R+
19: 01 98 a8 00 00 08 50 00 00 22 03 00 00 81 a4 00 00 03 e8 00 00 03 e8 00 00  ......P.."...............
32: 00 0c b6 6b a0 6d 31 5d 46 28 0b b0 9d 54 61 4c c5 2d 16 77 80 9f 00 09 66  ...k.m1]F(...TaL.-.w....f
4b: 69 6c 65 31 2e 74 78 74 00 54 52 45 45 00 00 00 19 00 31 20 30 0a 1f 53 c0  ile1.txt.TREE.....1 0..S.
64: 33 2b 89 b8 ad 3e 42 da 49 41 b7 9c 41 86 83 03 98 c1 7a f2 f8 9d 26 d1 59  3+...>B.IA..A.....z...&.Y
7d: 05 4d 62 72 a0 39 f0 11 5b cb a2 40                                         .Mbr.9..[..@
<<< /home/user/non-bare/.git/index

>>> /home/user/non-bare/.git/COMMIT_EDITMSG (UTF-8: 14 bytes)
1: second commit
<<< /home/user/non-bare/.git/COMMIT_EDITMSG

>>> /home/user/non-bare/.git/config (UTF-8: 92 bytes)
1: [core]
2:     repositoryformatversion = 0
3:     filemode = true
4:     bare = false
5:     logallrefupdates = true
<<< /home/user/non-bare/.git/config

>>> /home/user/non-bare/.git/HEAD (UTF-8: 21 bytes)
1: ref: refs/heads/main
<<< /home/user/non-bare/.git/HEAD

>>> /home/user/non-bare/.git/refs/heads/main (UTF-8: 41 bytes)
1: 0b725c4a9b5e9cdf54071807690a3a2f35f2a3d6
<<< /home/user/non-bare/.git/refs/heads/main

>>> /home/user/non-bare/.git/logs/HEAD (UTF-8: 319 bytes)
1: 0000000000000000000000000000000000000000 21590f740c9cb696bf7b207fe9c8114be9283fc7 Some User
   <some.user@example.org> 1765488030 +0100    commit (initial): first commit
2: 21590f740c9cb696bf7b207fe9c8114be9283fc7 0b725c4a9b5e9cdf54071807690a3a2f35f2a3d6 Some User
   <some.user@example.org> 1765488476 +0100    commit: second commit
<<< /home/user/non-bare/.git/logs/HEAD

>>> /home/user/non-bare/.git/logs/refs/heads/main (UTF-8: 319 bytes)
1: 0000000000000000000000000000000000000000 21590f740c9cb696bf7b207fe9c8114be9283fc7 Some User
   <some.user@example.org> 1765488030 +0100    commit (initial): first commit
2: 21590f740c9cb696bf7b207fe9c8114be9283fc7 0b725c4a9b5e9cdf54071807690a3a2f35f2a3d6 Some User
   <some.user@example.org> 1765488476 +0100    commit: second commit
<<< /home/user/non-bare/.git/logs/refs/heads/main

>>> /home/user/non-bare/.git/objects/b6/6ba06d315d46280bb09d54614cc52d1677809f (BINARY: 28 bytes)
00: 78 01 4b ca c9 4f 52 30 34 62 c8 4b 2d 57 48 ce cf 2b 49 cd 2b e1 02 00 43  x.K..OR04b.K-WH..+I.+...C
19: b9 06 92                                                                    ...
<<< /home/user/non-bare/.git/objects/b6/6ba06d315d46280bb09d54614cc52d1677809f

>>> /home/user/non-bare/.git/objects/1f/53c0332b89b8ad3e42da4941b79c4186830398 (BINARY: 53 bytes)
00: 78 01 2b 29 4a 4d 55 30 36 67 30 34 30 30 33 31 51 48 cb cc 49 35 d4 2b a9  x.+)JMU06g040031QH..I5.+.
19: 28 61 d8 96 bd 20 d7 30 d6 4d 83 7b c3 dc 90 44 9f a3 ba 62 e5 0d f3 01 39  (a... .0.M.{...D...b....9
32: 6d 0f 0a                                                                    m..
<<< /home/user/non-bare/.git/objects/1f/53c0332b89b8ad3e42da4941b79c4186830398

>>> /home/user/non-bare/.git/objects/c3/6defc2a7e6fab61af1e1f631af8bb5cca95ed1 (BINARY: 53 bytes)
00: 78 01 2b 29 4a 4d 55 30 36 67 30 34 30 30 33 31 51 48 cb cc 49 35 d4 2b a9  x.+)JMU06g040031QH..I5.+.
19: 28 61 10 57 95 a8 57 e0 d4 2d 3d f3 7e 5e 68 a9 b2 fc 7e ab fe d5 1c 00 26  (a.W..W..-=.~^h...~.....&
32: e2 0e 27                                                                    ..'
<<< /home/user/non-bare/.git/objects/c3/6defc2a7e6fab61af1e1f631af8bb5cca95ed1

>>> /home/user/non-bare/.git/objects/21/590f740c9cb696bf7b207fe9c8114be9283fc7 (BINARY: 129 bytes)
00: 78 01 9d 8d 41 0a c2 30 10 00 3d e7 15 7b 17 4a d6 98 34 05 91 fe 41 7c c0  x...A..0..=..{.J..4...A|.
19: 66 bb d1 82 21 92 a4 d0 e7 1b f4 07 de e6 32 33 9c 53 5a 1b e0 38 1d 5a 11  f...!.........23.SZ..8.Z.
32: 01 36 6e 91 c8 27 1a c5 45 0a 0e 29 a2 60 74 a6 83 0f c1 32 d3 64 65 41 45  .6n..'..E..).`t....2.deAE
4b: 5b 7b e6 02 b7 9c 04 ee 55 0a 5c 6a c7 61 eb 38 cb 4e e9 fd 92 21 97 c7 b5  [{......U.\j.a.8.N...!...
64: a7 9d 3d 7b af 8d 86 a3 46 ad 15 7f 97 ad 2b 7f c8 2a ae a5 36 f8 35 d4 07  ..={....F.....+..*..6.5..
7d: b6 89 3b f9                                                                 ..;.
<<< /home/user/non-bare/.git/objects/21/590f740c9cb696bf7b207fe9c8114be9283fc7

>>> /home/user/non-bare/.git/objects/17/25187f20092d75ccef9e5575231fbf3a8fab08 (BINARY: 31 bytes)
00: 78 01 4b ca c9 4f 52 30 34 65 48 ce cf 2b 49 cd 2b 51 48 cb cc 49 55 30 e4  x.K..OR04eH..+I.+QH..IU0.
19: 02 00 5a 9f 07 3c                                                           ..Z..<
<<< /home/user/non-bare/.git/objects/17/25187f20092d75ccef9e5575231fbf3a8fab08

>>> /home/user/non-bare/.git/objects/0b/725c4a9b5e9cdf54071807690a3a2f35f2a3d6 (BINARY: 162 bytes)
00: 78 01 9d ce 4d 0a c2 30 10 86 61 d7 39 45 f6 42 c9 5f 93 19 10 f1 0e e2 01  x...M..0..a.9E.B._.......
19: 92 e9 44 05 db 94 34 05 8f 6f d0 1b b8 7b 37 cf c7 47 65 9e 9f 4d 1a 03 87  ..D...4..o...{7..Ge..M...
32: 56 99 a5 ce a3 25 65 ad 49 80 09 e2 64 d9 99 29 3a 74 3a 05 24 a7 c1 83 55  V....%e.I...d..):t:.$...U
4b: 16 41 ac b1 f2 d2 a1 1e 51 e5 e0 14 21 25 8f 3e e5 90 8c 0a 99 91 40 6b 97  .A......Q...!%.>......@k.
64: 18 0d d8 4c 41 c4 bd 3d 4a 95 d7 32 b3 bc 6d 5c e5 69 eb 39 ec 3d 2f fc 8e  ...LA..=J..2..m\.i.9.=/..
7d: f3 fa e2 a1 d4 fb 59 ea e0 47 07 e0 82 97 47 a5 95 12 f4 bd d8 3a f9 03 8b  ......Y..G....G......:...
96: 8d a9 2c 93 fc 8d 88 0f f8 a4 47 bc                                         ..,.......G.
<<< /home/user/non-bare/.git/objects/0b/725c4a9b5e9cdf54071807690a3a2f35f2a3d6
```

Let's follow the chain again:

```text
user@host:~/non-bare$ git log -1
commit 0b725c4a9b5e9cdf54071807690a3a2f35f2a3d6 (HEAD -> main)
Author: Some User <some.user@example.org>
Date:   Thu Dec 11 22:27:56 2025 +0100

    second commit
user@host:~/non-bare$ git cat-file -p 0b725c4a9b5e9cdf54071807690a3a2f35f2a3d6
tree 1f53c0332b89b8ad3e42da4941b79c4186830398
parent 21590f740c9cb696bf7b207fe9c8114be9283fc7
author Some User <some.user@example.org> 1765488476 +0100
committer Some User <some.user@example.org> 1765488476 +0100

second commit
user@host:~/non-bare$ git cat-file -p 1f53c0332b89b8ad3e42da4941b79c4186830398
100644 blob b66ba06d315d46280bb09d54614cc52d1677809f    file1.txt
user@host:~/non-bare$ git cat-file -p b66ba06d315d46280bb09d54614cc52d1677809f
new content
```

Note the `parent` entry for commit `0b725c4a9b5e9cdf54071807690a3a2f35f2a3d6` which is `21590f740c9cb696bf7b207fe9c8114be9283fc7`: the SHA-1 of our previous commit. You can follow this (the objects still exist) and then find out the same objects we did before.

Notice: we now have two different objects for `file1.txt`:

1. First commit: `1725187f20092d75ccef9e5575231fbf3a8fab08`
2. Second commit: `b66ba06d315d46280bb09d54614cc52d1677809f`

This is the history concept of Git: normal commits only add new objects but do not remove older versions. The new version becomes a new object next to the existing object, see the [Object Database][git_object_database] documentation.

## Inspiration

This article is inspired and based on these resources:

- [Git Reference][git_reference]
- [Pro Git Book][pro_git_book]
- [Wikipedia - Git][wikipedia_git]
- [YouTube - LearnThatStack - Git Will Finally Make Sense After This][learnthatstack_git_makes_sense]
- [Julia Evans - In a git repository, where do your files live?][julia_evans_where_do_git_files_live]
- [Julia Evans - Do we think of git commits as diffs, snapshots, and/or histories?][julia_evans_think_of_git]
- [GeeksforGeeks - Top 10 GitHub Alternatives That You Can Consider][geeksforgeeks_top_10_github_alternatives]
- [OpenGenius - What is Git's description file?][opengenius_gits_description_file]
- [dump_file_tree.py]({{< param "github.benhattem_nl" >}}blob/main/content/posts/202512/git_under_the_hood/dump_file_tree.py)

[bitbucket]: https://bitbucket.org/
[geeksforgeeks_top_10_github_alternatives]: https://www.geeksforgeeks.org/blogs/top-10-github-alternatives-that-you-can-consider/
[git_blob_object]: https://git-scm.com/docs/user-manual.html#blob-object
[git_branch]: https://git-scm.com/docs/git-branch
[git_cat_file_p]: https://git-scm.com/docs/git-cat-file#Documentation/git-cat-file.txt--p
[git_cat_file_t]: https://git-scm.com/docs/git-cat-file#Documentation/git-cat-file.txt--t
[git_cat_file]: https://git-scm.com/docs/git-cat-file
[git_clone]: https://git-scm.com/docs/git-clone
[git_commit_object]: https://git-scm.com/docs/user-manual.html#commit-object
[git_commit]: https://git-scm.com/docs/git-commit
[git_hooks]: https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks
[git_index_format]: https://git-scm.com/docs/gitformat-index
[git_index]: https://git-scm.com/docs/user-manual.html#Documentation/user-manual.txt-index
[git_init_bare]: https://git-scm.com/docs/git-init#Documentation/git-init.txt---bare
[git_init]: https://git-scm.com/docs/git-init
[git_log]: https://git-scm.com/docs/git-log
[git_ls_files_stage]: https://git-scm.com/docs/git-ls-files#Documentation/git-ls-files.txt---stage
[git_object_database]: https://git-scm.com/docs/user-manual.html#the-object-database
[git_on_a_server]: https://git-scm.com/book/en/v2/Git-on-the-Server-Getting-Git-on-a-Server.html#_getting_git_on_a_server
[git_reference]: https://git-scm.com/docs
[git_reflog]: https://git-scm.com/docs/git-reflog
[git_show]: https://git-scm.com/docs/git-show
[git_status]: https://git-scm.com/docs/git-status
[git_template_directory]: https://git-scm.com/docs/git-init#_template_directory
[git_tree_objects]: https://git-scm.com/docs/user-manual.html#tree-object
[git]: https://git-scm.com/
[gitea]: https://about.gitea.com/
[gitlab]: https://gitlab.com/
[julia_evans_think_of_git]: https://jvns.ca/blog/2024/01/05/do-we-think-of-git-commits-as-diffs--snapshots--or-histories/
[julia_evans_where_do_git_files_live]: https://jvns.ca/blog/2023/09/14/in-a-git-repository--where-do-your-files-live-/
[learnthatstack_git_makes_sense]: https://youtu.be/Ala6PHlYjmw
[opengenius_gits_description_file]: https://iq.opengenus.org/git-description-file/
[pro_git_book_object_storage]: https://git-scm.com/book/en/v2/Git-Internals-Git-Objects#_object_storage
[pro_git_book]: https://git-scm.com/book/en/v2
[sourceforge]: https://sourceforge.net/
[ubuntu]: https://ubuntu.com/
[wikipedia_git]: https://en.wikipedia.org/wiki/Git
[wikipedia_github]: https://en.wikipedia.org/wiki/GitHub
[wikipedia_linus_torvalds]: https://en.wikipedia.org/wiki/Linus_Torvalds
[wikipedia]: https://www.wikipedia.org/
[windows_wsl]: https://learn.microsoft.com/en-us/windows/wsl/install
