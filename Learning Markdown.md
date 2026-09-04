---
title: Learning Markdown
tags: [onboarding]

---

# Learning Markdown
If you're new to Markdown and just starting to explore its capabilities, this guide is for you. Here you'll learn the basics, from simple text formatting to creating lists and more. By the end, you'll have the skills you need to write clean and structured documents with ease. 

The Markdown syntax will be written in the `code blocks` and an example of how it will appear is shown underneath.

With that, let's get started!

## What we'll cover
- [Markdown syntax](#Markdown-syntax)
- [Text style](#Text-style)
- [Tables](#Tables)
- [Table of contents](#Table-of-contents)
- [Edit vs View pages](#Edit-vs-View-pages)
- [Further learning](#Further-learning)

## Markdown syntax
### Unordered list
Syntax: `- unordered list`
- unordered list
### Ordered list
Syntax: `1. ordered list`
1. ordered list
### Task
Syntax: `- [ ] task`
- [ ] task

:::success
>[!Tip] Pressing  <kbd>Tab</kbd>  within a line will achieve the effect of a sublist.
>Edit according to your needs.

1. order list
    - unorder list
2. order list
    - [ ] task
:::

### Quote
Syntax: `> quote`
> quote
### Add editing time
Syntax: Enter `>[]` , move your mouse to the right and a menu (second option) will appear allowing you to insert the current time in the document.

Just like this :point_down:
>[time=Wed, Oct 30, 2024 8:23 PM]

### Quote alert
Syntax: Type `>[!]` and move your cursor after the`!` (if it's not already. From there, type or select either `Note`, `Tip`, `Important`, `Warning`, or `Caution`.

>[!Note]

>[!Tip]

>[!Important]

>[!Warning]

>[!Caution]

### Color blocks
Use these color blocks to emphasize important information. Simply replace the text after ``:::`` with ``info/success/warning/danger``, and the text editor will do the rest.

Syntax:
```
:::warning
text
:::
```

Color blocks will look like these :point_down: 
:::warning
:warning: Warnings
:::

:::danger
:radioactive_sign: Danger
:::

:::info
:information_source: Info
:::

:::success
 :100: Success
:::


### Hyperlink
Syntax: `[Display name](URL)`
[Display name](URL)


## Text style
### Headers

Put `#` at the beginning of a line and it becomes a header. Two `#`s create a level 2 header, and so on.

```
# text

## text

### text

#### text

##### text

###### text
```

### Bold
Syntax: `**bold**`
**bold**

### Italic
Syntax: `_italics_`
_italics_

### Literals
Syntax: Wrap the text with \` \` before and after.
`  Literal example  `
### Strikethrough
Syntax: `~~strikethrough~~`
~~strikethrough~~

### Highlight
Syntax: `==highlight==`
==highlight==

### Superscripts
Syntax: `21^th^ Century`
21^th^ Century

### Subscripts
Syntax: `H~2~O`
H~2~O

### Code block (HTML, Python, Markdown, CSS, etc.)

1. Use ` ``` `  to wrap the syntax on the first and last lines.
2. You can specify the type of language in the code block, e.g. html, javascript, python, markdown.
3. Just like this :point_down: 
    ```
    ```python
      print('Hello, world!')
      # See if you can set arbitrary line number or 
      # change syntax highlighting for different language
      # in this code block.    
    ```
4. Then you can move the mouse to the right of the language name, and use the menu to select adding line number, auto-wrap[^auto-wrap], or no effect at all.

This is what it looks like after rendering :point_down: 

```python=6
  print('Hello, world!')
  # See if you can set arbitrary line number or 
  # change syntax highlighting for different language
  # in this code block.
```

## We value your feedback!
Did you find this guide helpful? Answer one question in [this survey](https://tally.so/r/mV16qN) and let us know.

## Tables
Creating tables with Markdown can be messy, so we created a tool to make it easier. Simply click the Table icon in the toolbar at the top of the text editor.

![image](https://hackmd.io/_uploads/SJss0x73R.png)

| Column 1 | Column 2 | Column 3 |
|:-------- |:--------:| --------:|
| Some     |  thing   |     nice |
| Text     |   Text   |     Text |

Then, if you click on any cell within the table, the Table Editing Mode appears within the toolbar at the top of the page. 

[ → Learn more about creating a table here](https://hackmd.io/c/tutorials/%2Fs%2Fhow-to-create-table?utm_source=prepopulatednote&utm_medium=editor&utm_campaign=markdownsyntaxtutorial&utm_content=tutorial)

### Paste a table from Excel
You can also paste a table directly from Excel.

Simply select "Enable smart paste" in the text editor settings and you're set.

![PasteTable_HackMD](https://hackmd.io/_uploads/r16n7CLg1g.png)

## Table of contents

You can type `[toc]` to add a table of contents of your note as below:

[toc]

:::info
:bulb: **Navigating Menu**

If it's not already shown, you can bring up the table of contents by clicking the `☰` icon at the bottom-left of the View pane:

<img style="display:block;margin:20px auto;padding:1px;border:1px #eee;width:90%;" src="https://hackmd.io/_uploads/Bk3WLW4D0.gif" />
:::

## We value your feedback!
Did you find this guide helpful? Answer one question in [this survey](https://tally.so/r/mV16qN) and let us know.

## Edit vs View pages
#### Edit page
The Edit page of the HackMD editor is where all the magic happens -- it's your place for writing and formatting content with Markdown. 
![image](https://hackmd.io/_uploads/SyYgxv011x.png)

#### View page
The View page of the HackMD editor displays how your note will be rendered; a display of the formatted text, including headings, links, and images. It's a great way to ensure your content appears exactly as you intend before sharing or publishing.

You can jump back into editing at any time by clicking the `🖌️ Edit` button at the top right-hand corner of the page.

![image](https://hackmd.io/_uploads/BJTRkwCyJe.png)

:::success
:bulb: **Three modes in your editor**

Please locate these three icons at the top of HackMD. Here you can toggle between Edit/Both/View mode (from left to right).

![image](https://hackmd.io/_uploads/SylF_e4vR.png =150x)

We like to set it to Both mode so that you can take notes in Markdown in the left pane and see how it renders in the right pane.
:::

## Further learning
Want to learn more ways you can use HackMD? Check out the Beginner and Expert Guides in your workspace. 

The Beginner Guide covers:
- Workspace & sidebar
- Personal workspace
- Create a note
- Start with a template
- Insert images & gifs
- Comments
- Suggest edit
- Share & set permissions
- Publishing

The Expert Guide covers:
- Team workspace
- Sync with GitHub
- API calls
- Book mode
- Custom templates
- Embed notes
- LaTeX & MathJax
- UML diagrams

Before you go, HackMD has an official user manual with instructions for all its features!

In our tutorial book, you'll find detailed guides to all the main features of HackMD that boost your productivity.

### :point_right: [HackMD Tutorial Book](https://hackmd.io/c/tutorials/%2Fs%2Ftutorials?utm_source=prepopulatednote&utm_medium=editor&utm_campaign=markdownsyntaxtutorial&utm_content=tutorial) :point_left:

Don't want to miss the latest news and feature updates from HackMD? Be sure to follow our social channels or join us on Discord.

- :mailbox: support@hackmd.io
- <i class="fa fa-file-text"></i> [X (Twitter)](https://x.com/hackmdio)
- <i class="fa fa-file-text"></i> [Facebook](https://www.facebook.com/hackmdio)
- <i class="fa fa-file-text"></i> [LinkedIn](https://www.linkedin.com/company/hackmd)
- <i class="fa fa-file-text"></i> [Discord](https://discord.gg/rAkfPd5Z)


## We value your feedback!
Did you find this guide helpful? Answer one question in [this survey](https://tally.so/r/mV16qN) and let us know.


[^auto-wrap]:The system will automatically line-break 'Code block text that exceeds the width of the document' so that the content of the code block can be displayed in its entirety without the need to roll the scroll wheel to view it.
