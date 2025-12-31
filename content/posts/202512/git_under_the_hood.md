+++
date = "2025-12-11T22:33:16+01:00"
draft = false
title = "Git under the hood"
tags = ["git", "dvcs"]
+++
You probably know [Git][git] and might be aware of the (hidden) `.git` folder where the actual repository lives. Have you ever looked under the hood? Ever felt the need to know how Git does this magical thing with [`clone`][git_clone], [`commit`][git_commit], [`branch`][git_branch], etc.? What happens in the `.git` folder when you add a file? This article explores, for some of the standard operations, what really happens in the `.git` folder when a command is issued. Let's see how deep the rabbit hole goes!

<!--more-->
First of all, as a reminder: [Git][wikipedia_git] and [GitHub][wikipedia_github] are not the same. According to [Wikipedia][wikipedia]: "[Git][wikipedia_git] is a _distributed version control software system_ originally created by [Linus Torvalds][wikipedia_linus_torvalds] for version control in the development of the Linux kernel. [GitHub][wikipedia_github] is a _proprietary developer platform_ that allows developers to create, store, manage, and share their code." The only connection between the two is that [GitHub][wikipedia_github] uses [Git][wikipedia_git]. The same goes for sites like [GitLab][gitlab], [Bitbucket][bitbucket], [SourceForge][sourceforge], [AWS CodeCommit](https://aws.amazon.com/codecommit/) and even [Gitea][gitea]. Although they all use [Git][wikipedia_git] as repository, they are based on and add layers upon [Git][wikipedia_git] but are not the same.

For this article you should have basic Git knowledge: know terminology like repository, commit, branch, HEAD, index, etc. In case you need a refresher, search for "basic git tutorial" in your favorite search engine (or ask an LLM). Examples in this article are from the Python 3.14 Docker image (`python:3.14-slim` based on Debian Trixie) using Git version 2.47.3.

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
    86846      4 drwxr-xr-x   3 user     user         4096 Dec 31 14:22 .
    86853      4 drwxr-xr-x   7 user     user         4096 Dec 31 14:22 ./.git
    94690      4 -rw-r--r--   1 user     user           92 Dec 31 14:22 ./.git/config
    94688      4 drwxr-xr-x   4 user     user         4096 Dec 31 14:22 ./.git/refs
    94701      4 drwxr-xr-x   2 user     user         4096 Dec 31 14:22 ./.git/refs/tags
    94692      4 drwxr-xr-x   2 user     user         4096 Dec 31 14:22 ./.git/refs/heads
    94650      4 drwxr-xr-x   2 user     user         4096 Dec 31 14:22 ./.git/hooks
    94703      4 -rw-r--r--   1 user     user           21 Dec 31 14:22 ./.git/HEAD
    94682      4 drwxr-xr-x   2 user     user         4096 Dec 31 14:22 ./.git/info
    94686      4 drwxr-xr-x   2 user     user         4096 Dec 31 14:22 ./.git/branches
    94705      4 drwxr-xr-x   4 user     user         4096 Dec 31 14:22 ./.git/objects
    94707      4 drwxr-xr-x   2 user     user         4096 Dec 31 14:22 ./.git/objects/pack
    94709      4 drwxr-xr-x   2 user     user         4096 Dec 31 14:22 ./.git/objects/info
```

Let's dump the content of the files (using [dump_file_tree.py]({{< param "github.benhattem_nl" >}}blob/main/content/posts/202512/git_under_the_hood/dump_file_tree.py)):

```text
user@host:~/non-bare$ ../dump_file_tree.py --diff ../non-bare-diff.json
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
user@host:~/non-bare$ ../dump_file_tree.py --diff ../non-bare-diff.json
>>> /home/user/non-bare/file1.txt (UTF-8: 15 bytes)
1: content file 1
<<< /home/user/non-bare/file1.txt

>>> /home/user/non-bare/.git/index (BINARY: 104 bytes)
00: 44 49 52 43 00 00 00 02 00 00 00 01 69 55 25 b5 22 80 42 eb 69 55 25 b5 22  DIRC........iU%.".B.iU%."
19: 80 42 eb 00 00 08 30 00 01 53 37 00 00 81 a4 00 00 03 e8 00 00 03 e8 00 00  .B....0..S7..............
32: 00 0f 17 25 18 7f 20 09 2d 75 cc ef 9e 55 75 23 1f bf 3a 8f ab 08 00 09 66  ...%.. .-u...Uu#..:.....f
4b: 69 6c 65 31 2e 74 78 74 00 d7 db 7d 1e 18 9d 75 b5 54 be 55 60 27 86 4f f4  ile1.txt...}...u.T.U`'.O.
64: f6 92 e4 06                                                                 ....
<<< /home/user/non-bare/.git/index

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
00: .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. ..  DIRC........iU%.".B.iU%."
19: .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. ..  .B....0..S7..............
32: .. .. 17 25 18 7f 20 09 2d 75 cc ef 9e 55 75 23 1f bf 3a 8f ab 08 .. .. 66  ...%.. .-u...Uu#..:.....f
4b: 69 6c 65 31 2e 74 78 74 .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. ..  ile1.txt...}...u.T.U`'.O.
64: .. .. .. ..                                                                 ....
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
[main (root-commit) c4187f2] first commit
 1 file changed, 1 insertion(+)
 create mode 100644 file1.txt
user@host:~/non-bare$ git status
On branch main
nothing to commit, working tree clean
```

What has changed?

```text
user@host:~/non-bare$ ../dump_file_tree.py --diff ../non-bare-diff.json
>>> /home/user/non-bare/.git/index (BINARY: 137 bytes)
00: 44 49 52 43 00 00 00 02 00 00 00 01 69 55 25 b5 22 80 42 eb 69 55 25 b5 22  DIRC........iU%.".B.iU%."
19: 80 42 eb 00 00 08 30 00 01 53 37 00 00 81 a4 00 00 03 e8 00 00 03 e8 00 00  .B....0..S7..............
32: 00 0f 17 25 18 7f 20 09 2d 75 cc ef 9e 55 75 23 1f bf 3a 8f ab 08 00 09 66  ...%.. .-u...Uu#..:.....f
4b: 69 6c 65 31 2e 74 78 74 00 54 52 45 45 00 00 00 19 00 31 20 30 0a c3 6d ef  ile1.txt.TREE.....1 0..m.
64: c2 a7 e6 fa b6 1a f1 e1 f6 31 af 8b b5 cc a9 5e d1 f4 3c ac 53 ba 2e ae 7c  .........1.....^..<.S...|
7d: 03 21 85 01 9b 64 7e 1b 67 23 70 57                                         .!...d~.g#pW
<<< /home/user/non-bare/.git/index

>>> /home/user/non-bare/.git/COMMIT_EDITMSG (UTF-8: 13 bytes)
1: first commit
<<< /home/user/non-bare/.git/COMMIT_EDITMSG

>>> /home/user/non-bare/.git/refs/heads/main (UTF-8: 41 bytes)
1: c4187f2f386b9a87461ee1734dabbcff80f91744
<<< /home/user/non-bare/.git/refs/heads/main

>>> /home/user/non-bare/.git/logs/HEAD (UTF-8: 164 bytes)
1: 0000000000000000000000000000000000000000 c4187f2f386b9a87461ee1734dabbcff80f91744 Some User
   <some.user@example.org> 1767190718 +0100    commit (initial): first commit
<<< /home/user/non-bare/.git/logs/HEAD

>>> /home/user/non-bare/.git/logs/refs/heads/main (UTF-8: 164 bytes)
1: 0000000000000000000000000000000000000000 c4187f2f386b9a87461ee1734dabbcff80f91744 Some User
   <some.user@example.org> 1767190718 +0100    commit (initial): first commit
<<< /home/user/non-bare/.git/logs/refs/heads/main

>>> /home/user/non-bare/.git/objects/c3/6defc2a7e6fab61af1e1f631af8bb5cca95ed1 (BINARY: 53 bytes)
00: 78 01 2b 29 4a 4d 55 30 36 67 30 34 30 30 33 31 51 48 cb cc 49 35 d4 2b a9  x.+)JMU06g040031QH..I5.+.
19: 28 61 10 57 95 a8 57 e0 d4 2d 3d f3 7e 5e 68 a9 b2 fc 7e ab fe d5 1c 00 26  (a.W..W..-=.~^h...~.....&
32: e2 0e 27                                                                    ..'
<<< /home/user/non-bare/.git/objects/c3/6defc2a7e6fab61af1e1f631af8bb5cca95ed1

>>> /home/user/non-bare/.git/objects/c4/187f2f386b9a87461ee1734dabbcff80f91744 (BINARY: 128 bytes)
00: 78 01 9d 8d 41 0a c2 30 10 00 3d e7 15 7b 17 4a d6 d2 a4 01 11 ff 20 3e 60  x...A..0..=..{.J...... >`
19: b3 dd 68 c1 90 92 6c c1 e7 1b f4 07 de e6 32 33 5c 72 5e 15 d0 87 83 56 11  ..h...l.......23\r^....V.
32: e0 d1 2d 92 f8 44 5e 5c a2 e8 90 12 0a 26 37 76 98 63 9c 98 29 4c b2 a0 a1  ..-..D^\.....&7v.c..)L...
4b: 5d 9f a5 c2 ad 64 81 7b 93 0a e7 d6 71 d8 3b 5e e5 4d 79 7b c9 50 ea e3 d2  ]....d.{....q.;^.My{.P...
64: d3 ce 63 b0 1e 67 38 5a b4 d6 f0 77 a9 5d f9 43 36 69 ad 4d e1 d7 30 1f b8  ..c..g8Z...w.].C6i.M..0..
7d: 80 3c 03                                                                    .<.
<<< /home/user/non-bare/.git/objects/c4/187f2f386b9a87461ee1734dabbcff80f91744
```

The [`git log`][git_log] command shows:

```text
user@host:~/non-bare$ git log
commit c4187f2f386b9a87461ee1734dabbcff80f91744 (HEAD -> main)
Author: Some User <some.user@example.org>
Date:   Wed Dec 31 15:18:38 2025 +0100

    first commit
```

Summarized:

- The index `.git/index` is modified, a `TREE` is added.
- The commit message is stored in `.git/COMMIT_EDITMSG` (nice to know, but not that interesting).
- Logs are created: `.git/logs/HEAD` and `.git/logs/refs/heads/main`. This is used for [`git log`][git_log] and [`git reflog`][git_reflog], we will not explorer this further here.
- Two new objects are created: `.git/objects/c3/6defc2a7e6fab61af1e1f631af8bb5cca95ed1` and `.git/objects/c4/187f2f386b9a87461ee1734dabbcff80f91744`.
- Our `main` branch is created in `.git/refs/heads/main` (and `HEAD` points to this branch: `refs/heads/main`)

As shown in the [`git status`][git_status] output, we now have a `main` branch and `HEAD` points to this `main` branch. The commit SHA-1 itself (`c4187f2f386b9a87461ee1734dabbcff80f91744`) points to an object describing the commit content. To show this, we can use our Python script again but we may also use the standard [`git cat-file`][git_cat_file] command. First find out the type using the [`-t`][git_cat_file_t]:

```text
user@host:~/non-bare$ git cat-file -t c4187f2f386b9a87461ee1734dabbcff80f91744
commit
```

It's a [commit object][git_commit_object], we knew that already, but it's nice to get it confirmed. What does it contain? We can use the [`-p`][git_cat_file_p] option:

```text
user@host:~/non-bare$ git cat-file -p c4187f2f386b9a87461ee1734dabbcff80f91744
tree c36defc2a7e6fab61af1e1f631af8bb5cca95ed1
author Some User <some.user@example.org> 1767190718 +0100
committer Some User <some.user@example.org> 1767190718 +0100

first commit
```

It is linked to a [tree][git_tree_objects] which is again a Git object (`c36defc2a7e6fab61af1e1f631af8bb5cca95ed1`), let's have a look:

```text
user@host:~/non-bare$ git cat-file -p c36defc2a7e6fab61af1e1f631af8bb5cca95ed1
100644 blob 1725187f20092d75ccef9e5575231fbf3a8fab08    file1.txt
```

And there we have our file object `1725187...` again. So we go from `c4187f2f386b9a87461ee1734dabbcff80f91744` (commit) to `c36defc2a7e6fab61af1e1f631af8bb5cca95ed1` (tree) to `1725187f20092d75ccef9e5575231fbf3a8fab08` as a file in that tree. Note: trees are stored at multiple levels: a subdirectory will be stored as a separate tree (not shown here).

## Changing a file

Finally, lets quickly change a file and see what happens during the commit:

```bash
echo "new content" > file1.txt
git add -A .
git commit -m "second commit"
```

`.git` content:

```text
user@host:~/non-bare$ ../dump_file_tree.py --diff ../non-bare-diff.json
>>> /home/user/non-bare/file1.txt (UTF-8: 12 bytes)
1: new content
<<< /home/user/non-bare/file1.txt

>>> /home/user/non-bare/.git/index (BINARY: 137 bytes)
00: 44 49 52 43 00 00 00 02 00 00 00 01 69 55 32 8f 08 0d 17 5b 69 55 32 8f 08  DIRC........iU2....[iU2..
19: 0d 17 5b 00 00 08 30 00 01 53 37 00 00 81 a4 00 00 03 e8 00 00 03 e8 00 00  ..[...0..S7..............
32: 00 0c b6 6b a0 6d 31 5d 46 28 0b b0 9d 54 61 4c c5 2d 16 77 80 9f 00 09 66  ...k.m1]F(...TaL.-.w....f
4b: 69 6c 65 31 2e 74 78 74 00 54 52 45 45 00 00 00 19 00 31 20 30 0a 1f 53 c0  ile1.txt.TREE.....1 0..S.
64: 33 2b 89 b8 ad 3e 42 da 49 41 b7 9c 41 86 83 03 98 f6 8a 5b f9 2b ca 78 54  3+...>B.IA..A......[.+.xT
7d: 45 06 b6 98 80 4d c3 99 de f1 5c b5                                         E....M....\.
<<< /home/user/non-bare/.git/index

>>> /home/user/non-bare/.git/COMMIT_EDITMSG (UTF-8: 14 bytes)
1: second commit
<<< /home/user/non-bare/.git/COMMIT_EDITMSG

>>> /home/user/non-bare/.git/refs/heads/main (UTF-8: 41 bytes)
1: d40f72dfc8d0b0b5f75851a0ba841fe1af856059
<<< /home/user/non-bare/.git/refs/heads/main

>>> /home/user/non-bare/.git/logs/HEAD (UTF-8: 319 bytes)
1: 0000000000000000000000000000000000000000 c4187f2f386b9a87461ee1734dabbcff80f91744 Some User
   <some.user@example.org> 1767190718 +0100    commit (initial): first commit
2: c4187f2f386b9a87461ee1734dabbcff80f91744 d40f72dfc8d0b0b5f75851a0ba841fe1af856059 Some User
   <some.user@example.org> 1767191183 +0100    commit: second commit
<<< /home/user/non-bare/.git/logs/HEAD

>>> /home/user/non-bare/.git/logs/refs/heads/main (UTF-8: 319 bytes)
1: 0000000000000000000000000000000000000000 c4187f2f386b9a87461ee1734dabbcff80f91744 Some User
   <some.user@example.org> 1767190718 +0100    commit (initial): first commit
2: c4187f2f386b9a87461ee1734dabbcff80f91744 d40f72dfc8d0b0b5f75851a0ba841fe1af856059 Some User
   <some.user@example.org> 1767191183 +0100    commit: second commit
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

>>> /home/user/non-bare/.git/objects/d4/0f72dfc8d0b0b5f75851a0ba841fe1af856059 (BINARY: 161 bytes)
00: 78 01 9d 8e 41 0a c2 30 10 45 5d e7 14 b3 17 4a 26 13 9b 09 88 78 07 f1 00  x...A..0.E]....J&....x...
19: 49 3a 51 c1 36 25 4d c1 e3 5b f5 06 ee 1e 1f de e3 a7 32 8e 8f 06 c6 f0 ae  I:Q.6%M..[........2......
32: 55 11 c0 7c a0 a4 89 4c 64 1f 39 0c 24 d6 0c c1 7a 8b d1 f9 64 91 7b 26 4d  U..|...Ld.9.$...z...d.{&M
4b: 9e d5 1c aa 4c 0d 3e 93 cb 26 13 f7 d1 07 76 b6 47 11 74 64 87 10 63 ca 99  ....L.>..&....v.G.td..c..
64: 75 f6 e8 ac 55 61 6d f7 52 e1 52 46 81 eb 22 15 8e cb 86 dd ba e1 59 5e 61  u...Uam.R.RF..".......Y^a
7d: 9c 9f d2 95 7a 3b 01 ba de a1 47 64 82 bd 46 ad 55 fa 5e 6c 9b f2 87 ac 16  ....z;....Gd..F.U.^l.....
96: 49 65 1a e0 17 51 6f 14 1d 47 d4                                            Ie...Qo..G.
<<< /home/user/non-bare/.git/objects/d4/0f72dfc8d0b0b5f75851a0ba841fe1af856059
```

Let's follow the chain again:

```text
user@host:~/non-bare$ git log -1
commit d40f72dfc8d0b0b5f75851a0ba841fe1af856059 (HEAD -> main)
Author: Some User <some.user@example.org>
Date:   Wed Dec 31 15:26:23 2025 +0100

    second commit
user@host:~/non-bare$ git cat-file -p d40f72dfc8d0b0b5f75851a0ba841fe1af856059
tree 1f53c0332b89b8ad3e42da4941b79c4186830398
parent c4187f2f386b9a87461ee1734dabbcff80f91744
author Some User <some.user@example.org> 1767191183 +0100
committer Some User <some.user@example.org> 1767191183 +0100

second commit
user@host:~/non-bare$ git cat-file -p 1f53c0332b89b8ad3e42da4941b79c4186830398
100644 blob b66ba06d315d46280bb09d54614cc52d1677809f    file1.txt
user@host:~/non-bare$ git cat-file -p b66ba06d315d46280bb09d54614cc52d1677809f
new content
```

Note the `parent` entry for commit `d40f72dfc8d0b0b5f75851a0ba841fe1af856059` which is `c4187f2f386b9a87461ee1734dabbcff80f91744`: the SHA-1 of our previous commit. You can follow this (the objects still exist) and then find out the same objects we did before.

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
[wikipedia_git]: https://en.wikipedia.org/wiki/Git
[wikipedia_github]: https://en.wikipedia.org/wiki/GitHub
[wikipedia_linus_torvalds]: https://en.wikipedia.org/wiki/Linus_Torvalds
[wikipedia]: https://www.wikipedia.org/
