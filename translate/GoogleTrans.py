paper/paper.py                                                                                      0000664 0001750 0001750 00000000720 14115610424 011763  0                                                                                                    ustar   mqa                             mqa                                                                                                                                                                                                                    import GoogleTrans

def rmet(str):
    prgs = str.split('.\n')
    rt = ''
    for prg in prgs:
        rt += prg.replace('\r', '').replace('\n', ' ')
        rt += '.\n\n'
    return rt[:-3]

with open('paper.txt', 'r') as f:
    textList = rmet(f.read()).split('\n\n')

wf = open('paper-zh.txt', 'w')

for text in textList:
    _, _, targetText, _ = GoogleTrans.GoogleTrans().query(text, lang_to='zh-CN')
    wf.write(targetText)
    wf.write('\n\n')

wf.close()                                                paper/paper.txt                                                                                     0000664 0001750 0001750 00000065554 14115613430 012172  0                                                                                                    ustar   mqa                             mqa                                                                                                                                                                                                                    Abstract—Detecting semantically similar functions – a crucial
analysis capability with broad real-world security usages including
vulnerability detection, malware lineage, and forensics – requires
understanding function behaviors and intentions. However,
this task is challenging as semantically similar functions can be
implemented differently, run on different architectures, and compiled
with diverse compiler optimizations or obfuscations. Most
existing approaches match functions based on syntactic features
without understanding the functions’ execution semantics.
We present TREX, a transfer-learning-based framework, to
automate learning execution semantics explicitly from functions’
micro-traces (a form of under-constrained dynamic traces) and
transfer the learned knowledge to match semantically similar
functions. While such micro-traces are known to be too imprecise
to be directly used to detect semantic similarity, our key insight is
that these traces can be used to teach an ML model the execution
semantics of different sequences of instructions. We thus design
an unsupervised pretraining task, which trains the model to learn
execution semantics from the functions’ micro-traces without
any manual labeling or feature engineering effort. We then
develop a novel neural architecture, hierarchical Transformer,
which can learn execution semantics from micro-traces during
the pretraining phase. Finally, we finetune the pretrained model
to match semantically similar functions.
We evaluate TREX on 1,472,066 function binaries from 13
popular software projects. These functions are from different
architectures (x86, x64, ARM, and MIPS) and compiled with
4 optimizations (O0-O3) and 5 obfuscations. TREX outperforms
the state-of-the-art systems by 7.8%, 7.2%, and 14.3% in crossarchitecture,
optimization, and obfuscation function matching,
respectively, while running 8 faster. Our ablation studies
show that the pretraining task significantly boosts the function
matching performance, underscoring the importance of learning
execution semantics. Moreover, our extensive case studies
demonstrate the practical use-cases of TREX – on 180 real-world
firmware images with their latest version, TREX uncovers 16
vulnerabilities that have not been disclosed by any previous
studies. We release the code and dataset of TREX at https:
//github.com/CUMLSec/trex.
I. INTRODUCTION.
Semantic function similarity, which quantifies the behavioral
similarity between two functions, is a fundamental program
analysis capability with a broad spectrum of real-world security
usages, such as vulnerability detection [12], exploit generation
[5], tracing malware lineage [7], [41], and forensics [49].
For example, OWASP lists “using components with known
vulnerabilities” as one of the top-10 application security risks in
2020 [56]. Therefore, identifying similar vulnerable functions
in massive software projects can save significant manual effort.
When matching semantically similar functions for securitycritical
applications (e.g., vulnerability discovery), we often
have to deal with software at binary level, such as commercial
off-the-shelf products (i.e., firmware images) and legacy programs.
However, this task is challenging, as the functions’ highlevel
information (e.g., data structure definitions) are removed
during the compilation process. Establishing semantic similarity
gets even harder when the functions are compiled to run on
different instruction set architectures with various compiler
optimizations or obfuscated with simple transformations.
Recently, Machine Learning (ML) based approaches have
shown promise in tackling these challenges [25], [50], [77]
by learning robust features that can identify similar function
binaries across different architectures, compiler optimizations,
or even some types of obfuscation. Specifically, ML models
learn function representations (i.e., embeddings) from function
binaries and use the distance between the embeddings of
two functions to compute their similarity. The smaller the
distance, the more similar the functions are to each other. Such
approaches have achieved state-of-the-art results [25], [50], [77],
outperforming the traditional signature-based methods [79]
using hand-crafted features (e.g., number of basic blocks). Such
embedding distance-based strategy is particularly appealing for
large-scale function matching—taking only around 0.1 seconds
searching over one million functions [30].
Execution semantics. Despite the impressive progress, it
remains challenging for these approaches to match semantically
similar functions with disparate syntax and structure [51]. An
inherent cause is that the code semantics is characterized
by its execution effects. However, all existing learning-based
approaches are agnostic to program execution semantics,
training only on the static code. Such a setting can easily lead
a model into matching simple patterns, limiting their accuracy
when such spurious patterns are absent or changed [1], [61].
For instance, consider the following pair of x86 instrucations: mov eax,2;lea ecx,[eax+4] are semantically
equivalent to mov eax,2;lea ecx,[eax+eax*2]. An
ML model focusing on syntactic features might pick common
substrings (both sequences share the tokens mov, eax, lea,
ecx) to establish their similarity, which does not encode the
key reason of the semantic equivalence. Without grasping the
approximate execution semantics, an ML model can easily
learn such spurious patterns without understanding the inherent
cause of the equivalence: [eax+eax*2] computes the same
exact address as [eax+4] when eax is 2.
Limitations of existing dynamic approaches. Existing dynamic
approaches try to avoid the issues described above
by directly comparing the dynamic behaviors of functions
to determine similarity. As finding program inputs reaching
the target functions is an extremely challenging and timeconsuming
task, the prior works perform under-constrained
dynamic execution by initializing the function input states
(e.g., registers, memory) with random values and executing
the target functions directly [27]. Unfortunately, using such
under-constrained execution traces directly to compute function
similarities often result in many false positives [25]. For
example, providing random inputs to two different functions
with strict input checks might always trigger similar shallow
exception handling codes and might look spuriously similar.
Our approach. This paper presents TREX (TRansfer-learning
EXecution semantics) that trains ML models to learn the
approximate execution semantics from under-constrained dynamic
traces. Unlike prior works, which use such traces to
directly measure similarity, TREX pretrains the model on
diverse traces to learn each instruction’s execution effect in
its context. TREX then finetunes the model by transferring
the learned knowledge from pretraining to match semantically
similar functions (see Figure 1). Our extensive experiments
suggest that the approximately learned knowledge of execution
semantics in pretraining significantly boosts the accuracy
of matching semantically similar function binaries – TREX
excels in matching functions from different architectures,
optimizations, and obfuscations.
Our key observation is that while under-constrained dynamic
execution traces tend to contain many infeasible states, they still
encode precise execution effects of many individual instructions.
Thus, we can train an ML model to observe and learn the effect
of different instructions present across a large number of underconstrained
dynamic traces collected from diverse functions.
Once the model has gained an approximate understanding of
execution semantics of various instructions, we can train it to
match semantically similar functions by leveraging its learned
knowledge. As a result, during inference, we do not need to
execute any functions on-the-fly while matching them [45],
which saves significant runtime overhead. Moreover, our trained
model does not need the under-constrained dynamic traces to
match functions, it only uses the function instructions, but they
are augmented with rich knowledge of execution semantics.
In this paper, we extend micro-execution [34], a form of
under-constrained dynamic execution, to generate micro-traces
of a function across multiple instruction set architectures. A
micro-trace consists of a sequence of aligned instructions
and their corresponding program state values. We pretrain
the model on a large number of micro-traces gathered from
diverse functions as part of training data using the masked
language modeling (masked LM) task. Notably, masked LM
masks random parts in the sequence and asks the model to
predict masked parts based on their context. This design forces
the model to learn approximately how a function executes
to correctly infer the missing values, which automates learning
execution semantics without manual feature engineering.
Masked LM is also fully self-supervised [22] – TREX can thus
be trained and further improved with arbitrary functions found
in the wild.
To this end, we design a hierarchical Transformer [75] that
supports learning approximate execution semantics. Specifically,
our architecture models micro-trace values explicitly.
By contrast, existing approaches often treat the numerical
values as a dummy token [25], [50] to avoid prohibitively
large vocabulary size, which cannot effectively learn the rich
dependencies between concrete values that likely encode key
function semantics. Moreover, our architecture’s self-attention
layer is designed to model long-range dependencies in a
sequence [75] efficiently. Therefore, TREX can support roughly
170 longer sequence and runs 8 faster than existing neural
architectures, essential to learning embeddings of long function
execution traces.
We evaluate TREX on 1,472,066 functions collected from
13 popular open-source software projects across 4 architectures
(x86, x64, ARM, and MIPS) and compiled with 4 optimizations
(O0-O3), and 5 obfuscation strategies [78]. TREX outperforms
the state-of-the-art systems by 7.8%, 7.2%, and 14.3% in
matching functions across different architectures, optimizations,
and obfuscations, respectively. Our ablation studies show that
the pretraining task significantly improves the accuracy of
matching semantically similar functions (by 15.7%). We also
apply TREX in searching vulnerable functions in 180 realworld
firmware images developed by well-known vendors
and deployed in diverse embedded systems, including WLAN
routers, smart cameras, and solar panels. Our case study shows
that TREX helps find 16 CVEs in these firmware images,
which have not been disclosed in previous studies. We make
the following contributions.
 We propose a new approach to matching semantically
similar functions: we first train the model to learn approximate
program execution semantics from micro-traces,
a form of under-constrained dynamic traces, and then
transfer the learned knowledge to identify semantically
similar functions.
 We extend micro-execution to support different architectures
to collect micro-traces for training. We then develop
a novel neural architecture – hierarchical Transformer – to
learn approximate execution semantics from micro-traces.
 We implement TREX and evaluate it on 1,472,066 functions
from 13 popular software projects and libraries.
TREX outperforms the state-of-the-art tools by 7.8%,
7%, and 14.3%, in cross-architecture, optimization, and
obfuscation function matching, respectively, while running
up to 8 faster. Moreover, TREX helps uncover 16
vulnerabilities in 180 real-world firmware images with
the latest version that are not disclosed by previous
studies. We release the code and dataset of TREX at
https://github.com/CUMLSec/trex.
II. OVERVIEW.
In this section, we use the real-world functions as motivating
examples to describe the challenges of matching semantically
similar functions. We then overview our approach, focusing on
how our pretraining task (masked LM) addresses the challenges.
A. Challenging Cases.
We use three semantically equivalent but syntactically
different function pairs to demonstrate some challenges of
learning from only static code. Figure 2 shows the (partial)
assembly code of each function.
Cross-architecture example. Consider the functions in Figure
2a. Two functions have the same execution semantics as
both functions take the lower 12-bit of a register and compare
it to 0x80. Detecting this similarity requires understanding the
approximate execution semantics of and in x86 and lsl/lsr
in ARM. Moreover, it also requires understanding how the
values (i.e., 0xfff and 0x14) in the code are manipulated.
However, all existing ML-based approaches [50] only learn on
static code without observing each instruction’s real execution
effect. Furthermore, to mitigate the potentially prohibitive
vocabulary size (i.e., all possible memory addresses), existing
approaches replace all register values and memory addresses
with an abstract dummy symbol [26], [50]. They thus cannot
access the specific byte values to determine inherent similarity.
Cross-optimization example. Now consider two functions in
Figure 2b. They are semantically equivalent as [ebp+8] and
[esp+4] access the same memory location, i.e., the function’s
first argument pushed on the stack by the caller. To detect such
similarity, the model should understand push decreases the
stack pointer esp by 4. The model should also notice that
mov at line 2 assigns the decremented esp to ebp such
that ebp+8 in the upper function equals esp+4 in the lower
function. However, such dynamic information is not reflected
in the static code.
Cross-obfuscation example. Figure 2c demonstrates a simple
obfuscation by instruction substitution, which essentially
replaces eax+1 with eax-(-1). Detecting the equivalence
requires understanding approximately how arithmetic operations
such as xor, sub, and add, executes. However, static
information is not enough to expose such knowledge.
B. Pretraining Masked LM on Micro-traces.
This section describes how the pretraining task, masked
LM, on functions’ micro-traces encourages the model to learn
execution semantics. Although it remains an open research
question to explicitly prove certain knowledge is encoded by
such language modeling task [70], we focus on describing the
intuition behind the masked LM – why predicting masked codes
and values in micro-traces can help address the challenging
cases in Figure 2.
Masked LM. Recall the operation of masked LM: given a
function’s micro-trace (i.e., values and instructions), we mask
some random parts and train the model to predict the masked
parts using those not masked.
Note that pretraining with masked LM does not need any
manual labeling effort, as it only predicts the masked part in
the input micro-traces without any additional labeling effort.
Therefore, TREX can be trained and further improved with
a substantial number of functions found in the wild. The
benefit of this is that a certain instruction not micro-executed
in one function is highly likely to appear in at least one of the
other functions’ micro-traces, supporting TREX to approximate
diverse instructions’ execution semantics.
Masking register. Consider the functions in Figure 2c,
where they essentially increment the value at stack location
[rbp-0x2c] by 1. The upper function directly loads the value
to eax, increments by 1, and stores the value in eax back to
stack. The lower function, by contrast, takes a convoluted way
by first letting ecx to hold the value -1, and decrements eax
by ecx, and stores the value in eax back to stack.
We mask the eax at line 3 in the upper function. We
find that our pretrained model can correctly predict its name
and dynamic value. This implies the model understands the
semantics of add and can deduce the value of eax in line 3
after observing the value of eax in line 2 (before the addition
takes the effect). We also find the model can recover the values
of masked ecx in line 4 and eax in line 5, implying the
model understands the execution effect of xor and sub.
The understanding of such semantics can significantly
improve the robustness in matching similar functions – when
finetuned to match similar functions, the model is more likely
to learn to attribute the similarity to their similar execution
effects, instead of their syntactic similarity.
Masking opcode. Besides masking the register and its value,
we can also mask the opcode of an instruction. Predicting the
opcode requires the model to understand the execution effect
of each opcode. Consider Figure 2b, where we mask mov in
line 2 of upper function. We find our pretrained model predicts
mov with the largest probability (larger than the other potential
candidates such as add, inc, etc.).
To correctly predict the opcode, the model should have
learned several key aspects of the function semantics. First,
according to its context, i.e., the value of ebp at line 3 and
esp at line 2, it learns mov is most probable as it assigns
the value of esp to ebp. Other opcodes are less likely as
their execution effect conflicts with the observed resulting
register values. This also implicitly implies the model learns the
approximate execution semantics of mov. Second, the model
also learns the common calling convention and basic syntax
of x86 instructions, e.g., only a subset of opcodes accept two
operands (ebp,esp). It can thus exclude many syntactically
impossible opcodes such as push, jmp, etc.
The model can thus infer ebp (line 3 of upper function)
equals to esp. The model may have also learned push
decrements stack pointer esp by 4 bytes, from other masked
samples. Therefore, when the pretrained model is finetuned
to match the two functions, the model is more likely to learn
that the semantic equivalence is due to that [ebp+8] in the
upper function and [esp+4] in the lower function refer to
the same address, instead of their similar syntax.
Other masking strategies. Note that we are not constrained
by the number or the type of items (i.e., register, opcode,
etc.) in the instructions to mask, i.e., we can mask complete
instructions or even a consecutive sequence of instructions, and
we can mask dynamic values of random instructions’ inputoutput.
Moreover, the masking operation dynamically selects
random subsets of code blocks and program states at each
training iteration and on different training samples. As a result,
it enables the model to learn the diverse and composite effect
of the instruction sequence, essential to detecting similarity
between functions with various instructions. In this paper, we
adopt a completely randomized strategy to choose what part
of the micro-trace to mask with a fixed masking percentage
(see Section IV-C for details). However, we envision a quite
interesting future work to study a better (but still cheap) strategy
to dynamically choose where and how much to mask.
III. THREAT MODEL.
We assume no access to the debug symbols or source while
comparing binaries. Indeed, there exist many approaches to
reconstruct functions from stripped binaries [4], [6], [24], [62],
[72]. Moreover, we assume the binary can be readily disassembled,
i.e., it is not packed nor transformed by virtualizationbased
obfuscator [73], [74].
Semantic similarity. We consider two semantically similar
functions as having the same input-output behavior (i.e., given
the same input, two functions produce the same output). Similar
to previous works [25], [50], [77], we treat functions compiled
from the same source as similar, regardless of architectures,
compilers, optimizations, and obfuscation transforms.
IV. METHODOLOGY.
This section describes TREX’s design specifics, including
our micro-tracing semantics, our learning architecture’s details,
and pretraining and finetuning workflow.
A. Micro-tracing Semantics.
We implement micro-execution by Godefroid [34] to handle
x64, ARM, and MIPS, where the original paper only describes
x86 as the use case. In the following, we briefly explain how
we micro-execute an individual function binary, highlighting
the key algorithms in handling different types of instructions.
IR Language. To abstract away the complexity of different
architectures’ assembly syntax, we introduce a low-level
intermediate representation (IR) that models function assembly
code. We only include a subset of the language specifics to
illustrate the implementation algorithm. Figure 3 shows the
grammar of the IR. Note that the IR here only serves to
facilitate the discussion of our micro-tracing implementation.
In our implementation, we use real assembly instructions and
tokenize them as model’s input (Section IV-B).
Notably, we denote memory reads and writes by load(e)
and store(ev; ea) (i.e., store the value expression ev to
address expression ea), which generalize from both the loadstore
architecture (i.e., ARM, MIPS) and register-memory
architecture (i.e., x86). Both operations can take as input e
– an expression that can be an explicit hexadecimal number
(denoting the address or a constant), a register, or a result of an
operation on two registers. We use jmp to denote the general
jump instruction, which can be both direct or indirect jump (i.e.,
the expression ea can be a constant c or a register r). The jump
instruction can also be unconditional or conditional. Therefore,
the first parameter in jmp is the conditional expression ec
and unconditional jump will set ec to true. We represent
function invocations and returns by call and ret, where
call is parameterized by an expression, which can be an
address (direct call) or a register (indirect call).
Micro-tracing algorithm. Algorithm 1 outlines the basic steps
of micro-tracing a given function f. First, it initializes the
memory to load the code and the corresponding stack. It then
initializes all registers except the special-purpose register, such
as the stack pointer or the program counter. Then it starts
linearly executing instructions of f. We map the memory
address on-demand if the instruction access the memory (i.e.,
read/write). If the instruction reads from memory, we further
initialize a random value in the specific memory addresses. For
call/jump instructions, we first examine the target address and
skip the invalid jump/call, known as “forced execution” [63]. By
skipping unreachable jumps and calls, it can keep executing the
function till the end of the function and exposes more behaviors,
e.g., skipping potential input check exceptions. Since the nop
instructions can serve as padding between instructions within a
function, we simply skip nop. We terminate the micro-tracing
when it finishes executing all instructions, reaches ret, or
times out. Figure 13 and 14 demonstrate sample micro-traces
of real-world functions.
B. Input Representation.
Formally, given a function f (i.e., assembly code) and its
micro-trace t (by micro-executing f), we prepare the model
input x, consisting of 5 types of token sequence with the same
size n. Figure 4 shows the model input example and how they
are masked and processed by the hierarchical Transformer to
predict the corresponding output as a pretraining task.
Micro-trace code sequence. The first sequence xf is the
assembly code sequence: xf = fmov; eax;+; :::gn, generated
by tokenizing the assembly instructions in the micro-trace. We
treat all symbols appear in the assembly instructions as tokens.
Such a tokenization aims to preserve the critical hint of the
syntax and semantics of the assembly instructions. For example,
we consider even punctuation to be one of the tokens, e.g.,
“,”, “[”, “]”, as “,” implies the token before and after it as
destination and source of mov (in Intel syntax), respectively,
and “[” and “]” denote taking the address of the operands
reside in between them.
We take special treatment of numerical values appear in
the assembly code. Treating numerical values as regular text
tokens can incur prohibitively large vocabulary size, e.g., 232
number of possibilities on 32-bit architectures. To avoid this
problem, we move all numeric values to the micro-trace value
sequence (that will be learned by an additional neural network
as detailed in the following) and replace them with a special
token num (e.g., last token of input in Figure 4). With all
these preprocessing steps, the vocabulary size of xf across all
architectures is 3,300.
Micro-trace value sequence. The second sequence xt is the
micro-trace value sequence, where each token in xt is the
dynamic value from micro-tracing the corresponding code. As
discussed in Section II, we keep explicit values (instead of
a dummy value used by existing approaches) in xt. Notably,
we use the dynamic value for each token (e.g., register) in
an instruction before it is executed. For example, in mov
eax,0x8; mov eax,0x3, the dynamic value of the second
eax is 0x8, as we take the value of eax before mov
eax,0x3 is executed. For code token without dynamic value,
e.g., mov, we use dummy values (see below).
Position sequences. The position of each code and value
token is critical for inferring binary semantics. Unlike natural
language, where swapping two words can roughly preserve
the same semantic meaning, swapping two operands can
significantly change the instructions. To encode the inductive
bias of position into our model, we introduce instruction
position sequence xc and opcode/operand position sequence
xo to represent the relative positions between the instructions
and within each instruction. As shown in Figure 4, xc is a
sequence of integers encoding the position of each instruction.
All opcodes/operands within a single instruction share the same
value. xo is a sequence of integers encoding the position of
each opcode and operands within a single instruction.
Architecture sequence. Finally, we feed the model with an
extra sequence xa, describing the input binary’s instruction set
architecture. The vocabulary of xa consists of 4 architectures:
xa = fx86, x64, ARM, MIPSgn. This setting helps the model
to distinguish between the syntax of different architecture.
Encoding numeric values. As mentioned above, treating
concrete values as independent tokens can lead to prohibitively
large vocabulary size. We design a hierarchical input encoding
scheme to address this challenge. Specifically, let xti denote
the i-th value in xt. We represent xti as an (padded) 8-byte
fixed-length byte sequence xti =f0x00, ..., 0xffg8 ordered
in Big-Endian. We then feed xti to a 2-layer bidirectional
LSTM (bi-LSTM) and take its last hidden cell’s embedding as
the value representation ti = bi-LSTM(xti ). Here ti denotes
the output of applying the embedding to xti . To make the
micro-trace code tokens without dynamic values (e.g., opcode)
align with the byte sequence, we use a dummy sequence (##)
with the same length. Figure 4 (right-hand side) illustrates how
bi-LSTM takes the byte sequence and computes the embedding.
Such a design significantly reduces the vocabulary size as
now we have only 256 possible byte values to encode. Moreover,
bi-LSTM encodes the potential dependencies between
high and low bytes within a single value. This setting thus
supports learning better relationships between different dynamic
values (e.g., memory region and offset) as opposed to treating
all values as dummy tokens [71].                                                                                                                                                    paper/paper-zh.txt                                                                                  0000664 0001750 0001750 00000142531 14116010471 012575  0                                                                                                    ustar   mqa                             mqa                                                                                                                                                                                                                    Abstract—Detecting semantically similar functions – a crucial analysis capability with broad real-world security usages including vulnerability detection, malware lineage, and forensics – requires understanding function behaviors and intentions.
摘要检测语义类似的功能-具有广泛的现实安全用途的重要分析能力，包括漏洞检测，恶意软件血统和取证-需要了解函数行为和意图。
However, this task is challenging as semantically similar functions can be implemented differently, run on different architectures, and compiled with diverse compiler optimizations or obfuscations.
但是，此任务具有具有挑战性，因为语义类似的功能可以不同地实现，在不同的体系结构上运行，并以不同的编译器优化或混淆编译。
Most existing approaches match functions based on syntactic features without understanding the functions’ execution semantics.
大多数现有方法匹配基于语法特征的函数，而无需了解函数的执行语义。

We present TREX, a transfer-learning-based framework, to automate learning execution semantics explicitly from functions’ micro-traces (a form of under-constrained dynamic traces) and transfer the learned knowledge to match semantically similar functions.
我们呈现TREX，一种基于传输学习的框架，从功能的微迹（一种被限制的动态迹线的形式）明确自动化学习执行语义，并传送学习知识以匹配语义上类似的功能。
While such micro-traces are known to be too imprecise to be directly used to detect semantic similarity, our key insight is that these traces can be used to teach an ML model the execution semantics of different sequences of instructions.
虽然已知这种微迹情况过于不精确地直接用于检测语义相似性，但我们的主要洞察力是这些迹线可用于教导ML模型不同指令序列的执行语义。
We thus design an unsupervised pretraining task, which trains the model to learn execution semantics from the functions’ micro-traces without any manual labeling or feature engineering effort.
因此，我们设计了一个无人监测的预测任务，该任务将模型列出了从功能的微迹中学习执行语义，而无需任何手动标签或特征工程工作。
We then develop a novel neural architecture, hierarchical Transformer, which can learn execution semantics from micro-traces during the pretraining phase.
然后，我们开发一种新型神经结构，等级变压器，可以在预先预测阶段学习来自微迹的执行语义。
Finally, we finetune the pretrained model to match semantically similar functions.
最后，我们芬特将佩带的模型匹配语义类似的功能。

We evaluate TREX on 1,472,066 function binaries from 13 popular software projects.
从13个流行的软件项目中评估1,472,066个功能二进制文件的TREX。
These functions are from different architectures (x86, x64, ARM, and MIPS) and compiled with 4 optimizations (O0-O3) and 5 obfuscations.
这些功能来自不同的架构（x86，x64，arm和mips），并用4个优化（o0-o3）和5个混淆编译。
TREX outperforms the state-of-the-art systems by 7.8%, 7.2%, and 14.3% in crossarchitecture, optimization, and obfuscation function matching, respectively, while running 8 faster.
TREX分别优于最先进的系统，分别在交叉结构，优化和混淆函数匹配中以7.8％，7.2％和14.3％匹配。
Our ablation studies show that the pretraining task significantly boosts the function matching performance, underscoring the importance of learning execution semantics.
我们的消融研究表明，预先预订任务显着提高了匹配性能的功能，强调了学习执行语义的重要性。
Moreover, our extensive case studies demonstrate the practical use-cases of TREX – on 180 real-world firmware images with their latest version, TREX uncovers 16 vulnerabilities that have not been disclosed by any previous studies.
此外，我们的广泛案例研究展示了TREX的实际用例-在180个现实世界固件图像中，TREXOffers未通过以前的研究披露的16个漏洞。
We release the code and dataset of TREX at https: //github.com/CUMLSec/trex.
我们在https：//github.com/cumlsec/trex中释放TREX的代码和数据集。

I. INTRODUCTION.
I.介绍。

Semantic function similarity, which quantifies the behavioral similarity between two functions, is a fundamental program analysis capability with a broad spectrum of real-world security usages, such as vulnerability detection [12], exploit generation [5], tracing malware lineage [7]
语义功能相似度，这量化了两个功能之间的行为相似性，是具有广泛的实际安全用途的基本程序分析能力，例如漏洞检测[12]，利用生成[5]，跟踪恶意软件谱系[7]
, [41], and forensics [49].
，[41]和法医[49]。

For example, OWASP lists “using components with known vulnerabilities” as one of the top-10 application security risks in 2020 [56].
例如，OWASP列出“使用具有已知漏洞的组件”作为2020年的前10个应用程序安全风险之一[56]。
Therefore, identifying similar vulnerable functions in massive software projects can save significant manual effort.
因此，在大规模软件项目中识别类似的易受攻击功能，可以节省重大的手动努力。

When matching semantically similar functions for securitycritical applications (e.g., vulnerability discovery), we often have to deal with software at binary level, such as commercial off-the-shelf products (i.e., firmware images) and legacy programs.
当匹配SecurityCritical应用程序的语义类似的功能时（例如，漏洞发现），我们经常必须在二进制级别处理软件，例如商业现货产品（即固件图像）和遗留程序。

However, this task is challenging, as the functions’ highlevel information (e.g., data structure definitions) are removed during the compilation process.
但是，此任务是具有挑战性的，因为在编译过程中删除了函数的函数高级信息（例如，数据结构定义）。
Establishing semantic similarity gets even harder when the functions are compiled to run on different instruction set architectures with various compiler optimizations or obfuscated with simple transformations.
在编译函数以在不同的指令集架构上运行时，建立语义相似性甚至更加困难，其中包含各种编译器优化或使用简单的转换混淆。

Recently, Machine Learning (ML) based approaches have shown promise in tackling these challenges [25], [50], [77] by learning robust features that can identify similar function binaries across different architectures, compiler optimizations, or even some types of obfuscation
最近，基于机器学习（ML）的方法在解决这些挑战[25]，[50]，[77]时，可以通过学习鲁棒功能来解决这些挑战，可以识别不同架构，编译器优化，甚至某种类型的混淆的类似功能二进制文件
.
。
Specifically, ML models learn function representations (i.e., embeddings) from function binaries and use the distance between the embeddings of two functions to compute their similarity.
具体而言，ML模型从功能二进制文件学习功能表示（即嵌入），并使用两个函数的嵌入之间的距离来计算它们的相似度。
The smaller the distance, the more similar the functions are to each other.
距离越小，函数彼此越多。
Such approaches have achieved state-of-the-art results [25], [50], [77], outperforming the traditional signature-based methods [79] using hand-crafted features (e.g., number of basic blocks).
这种方法已经实现了最先进的结果[25]，[50]，[77]，优于使用手工制作的特征（例如，基本块数）的传统签名的方法[79]。
Such embedding distance-based strategy is particularly appealing for large-scale function matching—taking only around 0.1 seconds searching over one million functions [30].
这种嵌入距离的策略对于大规模函数匹配特别吸引力-仅在一百万个功能中搜索约0.1秒[30]。

Execution semantics.
执行语义。
Despite the impressive progress, it remains challenging for these approaches to match semantically similar functions with disparate syntax and structure [51].
尽管进展令人印象深刻，但这些方法仍然有挑战性，以匹配不同的语法和结构的语义类似的功能[51]。
An inherent cause is that the code semantics is characterized by its execution effects.
固有原因是代码语义的特征在于其执行效果。
However, all existing learning-based approaches are agnostic to program execution semantics, training only on the static code.
但是，所有现有的基于学习的方法都是不可知的，用于编程执行语义，仅在静态代码上训练。
Such a setting can easily lead a model into matching simple patterns, limiting their accuracy when such spurious patterns are absent or changed [1], [61].
这种设置可以容易地引导模型成匹配简单的图案，限制了它们的准确性，当不存在或改变[1]，[61]时。

For instance, consider the following pair of x86 instrucations: mov eax,2;lea ecx,[eax+4] are semantically equivalent to mov eax,2;lea ecx,[eax+eax*2].
例如，考虑以下对X86的作用：MOVEAX，2;LEAECX，[EAX+4]是语义相当于MOVEAX，2;LEAECX，[EAX+EAX*2]。
An ML model focusing on syntactic features might pick common substrings (both sequences share the tokens mov, eax, lea, ecx) to establish their similarity, which does not encode the key reason of the semantic equivalence.
专注于句法特征的ML模型可能选择常见的子字符串（两个序列共享令牌MOV，EAX，LEA，ECX）以建立其相似性，这不会编码语义等效的关键原因。
Without grasping the approximate execution semantics, an ML model can easily learn such spurious patterns without understanding the inherent cause of the equivalence: [eax+eax*2] computes the same exact address as [eax+4] when eax is 2.
在没有掌握近似执行语义的情况下，ML模型可以容易地学习这种虚假模式而不了解当量的固有原因：[eax+eax*2]当EAx为2时计算与[EAX+4]相同的Actique地址。

Limitations of existing dynamic approaches.
现有动态方法的局限性。
Existing dynamic approaches try to avoid the issues described above by directly comparing the dynamic behaviors of functions to determine similarity.
现有的动态方法尝试通过直接比较功能的动态行为来避免上述问题来确定相似性。
As finding program inputs reaching the target functions is an extremely challenging and timeconsuming task, the prior works perform under-constrained dynamic execution by initializing the function input states (eg, registers, memory) with random values and executing the target functions directly [27]
作为达到目标功能的查找程序输入是一个非常具有挑战性和时序的任务，先前的作品通过初始化具有随机值的函数输入状态（例如，寄存器，存储器）并直接执行目标函数来执行欠约束动态执行。
.
。
Unfortunately, using such under-constrained execution traces directly to compute function similarities often result in many false positives [25].
不幸的是，使用这种下限的执行迹线直接计算函数相似度，通常会导致许多误报[25]。
For example, providing random inputs to two different functions with strict input checks might always trigger similar shallow exception handling codes and might look spuriously similar.
例如，为两个不同函数提供随机输入，严格输入检查可能始终触发类似的浅例外处理代码，并且可能看起来很类似。

Our approach.
我们的方法。
This paper presents TREX (TRansfer-learning EXecution semantics) that trains ML models to learn the approximate execution semantics from under-constrained dynamic traces.
本文介绍了列出ML模型的TREX（传送学习执行语义），以了解来自受限的动态迹线的近似执行语义。
Unlike prior works, which use such traces to directly measure similarity, TREX pretrains the model on diverse traces to learn each instruction’s execution effect in its context.
与先前的作品不同，它使用此类痕迹直接测量相似性，TREX预先绘制了不同迹线的模型，以了解其上下文中的每个指令的执行效果。
TREX then finetunes the model by transferring the learned knowledge from pretraining to match semantically similar functions (see Figure 1).
然后TREX通过将学习知识从预先预测转移以匹配语义上类似的功能来FineTunes来融合模型（参见图1）。
Our extensive experiments suggest that the approximately learned knowledge of execution semantics in pretraining significantly boosts the accuracy of matching semantically similar function binaries – TREX excels in matching functions from different architectures, optimizations, and obfuscations.
我们广泛的实验表明，预先预测中的执行语义的大致了解知识显着提高了匹配语义相似的功能二进制文件的准确性-来自不同架构，优化和混淆的匹配功能中的TREXExcel。

Our key observation is that while under-constrained dynamic execution traces tend to contain many infeasible states, they still encode precise execution effects of many individual instructions.
我们的关键观察是，虽然受限制的动态执行迹线倾向于包含许多不可行状态，但它们仍然编码许多单个指令的精确执行效果。

Thus, we can train an ML model to observe and learn the effect of different instructions present across a large number of underconstrained dynamic traces collected from diverse functions.
因此，我们可以训练ML模型来观察和学习不同指令在从各种功能中收集的大量欠信线的动态迹线的影响。

Once the model has gained an approximate understanding of execution semantics of various instructions, we can train it to match semantically similar functions by leveraging its learned knowledge.
一旦模型获得了对各种指示的执行语义的大致了解，我们就可以通过利用其学到的知识来训练它来匹配语义类似的功能。
As a result, during inference, we do not need to execute any functions on-the-fly while matching them [45], which saves significant runtime overhead.
因此，在推理期间，我们不需要在匹配它们[45]的同时随时执行任何功能，从而节省了大量的运行时开销。
Moreover, our trained model does not need the under-constrained dynamic traces to match functions, it only uses the function instructions, but they are augmented with rich knowledge of execution semantics.
此外，我们的培训模型不需要受限制的动态迹线来匹配函数，它只使用函数指令，但它们是丰富的执行语义知识。

In this paper, we extend micro-execution [34], a form of under-constrained dynamic execution, to generate micro-traces of a function across multiple instruction set architectures.
在本文中，我们扩展了微执行[34]，一种被限制的动态执行的形式，以在多个指令集架构中生成函数的微迹。
A micro-trace consists of a sequence of aligned instructions and their corresponding program state values.
微跟踪包括一系列对齐指令及其相应的程序状态值。
We pretrain the model on a large number of micro-traces gathered from diverse functions as part of training data using the masked language modeling (masked LM) task.
我们将模型预留在从各种功能中收集的大量微量迹线，作为使用屏蔽语言建模（屏蔽LM）任务的培训数据的一部分。
Notably, masked LM masks random parts in the sequence and asks the model to predict masked parts based on their context.
值得注意的是，屏蔽LM掩模序列中的随机部件，并询问模型基于其上下文预测屏蔽部分。
This design forces the model to learn approximately how a function executes to correctly infer the missing values, which automates learning execution semantics without manual feature engineering.
这种设计强制模型了解函数如何执行如何正确推断缺失值，无需手动功能工程，自动化学习执行语义。

Masked LM is also fully self-supervised [22] – TREX can thus be trained and further improved with arbitrary functions found in the wild.
蒙面LM也是完全自我监督的[22]-因此可以在野外发现的任意功能进行培训并进一步改善TREX。

To this end, we design a hierarchical Transformer [75] that supports learning approximate execution semantics.
为此，我们设计了一个支持学习近似执行语义的分层变换器[75]。
Specifically, our architecture models micro-trace values explicitly.
具体而言，我们的体系结构明确模拟微跟踪值。

By contrast, existing approaches often treat the numerical values as a dummy token [25], [50] to avoid prohibitively large vocabulary size, which cannot effectively learn the rich dependencies between concrete values that likely encode key function semantics.
相比之下，现有方法通常将数值视为伪令牌[25]，[50]以避免过大的词汇量，这不能有效地学习可能对关键函数语义的具体值之间的丰富依赖性。
Moreover, our architecture’s self-attention layer is designed to model long-range dependencies in a sequence [75] efficiently.
此外，我们的架构的自我注意层设计用于序列中的长距离依赖性[75]有效。
Therefore, TREX can support roughly 170 longer sequence and runs 8 faster than existing neural architectures, essential to learning embeddings of long function execution traces.
因此，TREX可以高出大约170个更长的序列，并且比现有的神经架构快8次，对于长函数执行迹线的学习嵌入至关重要。

We evaluate TREX on 1,472,066 functions collected from 13 popular open-source software projects across 4 architectures (x86, x64, ARM, and MIPS) and compiled with 4 optimizations (O0-O3), and 5 obfuscation strategies [78].
我们评估了从4架构（X86，X64，ARM和MIPS）的13个流行的开源软件项目收集的1,472,066函数上的TREX，并用4个优化（O0-O3）和5个混淆策略编译[78]。
TREX outperforms the state-of-the-art systems by 7.8%, 7.2%, and 14.3% in matching functions across different architectures, optimizations, and obfuscations, respectively.
TREX分别优于最先进的系统，分别在不同架构，优化和混淆的匹配功能中以7.8％，7.2％和14.3％。
Our ablation studies show that the pretraining task significantly improves the accuracy of matching semantically similar functions (by 15.7%).
我们的消融研究表明，预先预订任务显着提高了语义类似功能的准确性（15.7％）。
We also apply TREX in searching vulnerable functions in 180 realworld firmware images developed by well-known vendors and deployed in diverse embedded systems, including WLAN routers, smart cameras, and solar panels.
我们还将TREX应用于由众所周知的供应商开发的180个RealWorld固件图像中搜索弱势职能，并在不同的嵌入式系统中部署，包括WLAN路由器，智能摄像机和太阳能电池板。
Our case study shows that TREX helps find 16 CVEs in these firmware images, which have not been disclosed in previous studies.
我们的案例研究表明，TREX有助于在这些固件图像中找到16个CVVE，该图像尚未在以前的研究中披露。
We make the following contributions.
我们提出以下贡献。

We propose a new approach to matching semantically similar functions: we first train the model to learn approximate program execution semantics from micro-traces, a form of under-constrained dynamic traces, and then transfer the learned knowledge to identify semantically similar functions.
我们提出了一种新方法来匹配语义上类似的功能：我们首先培训模型，从微迹中学习近似程序执行语义，这是一个受限的动态迹线的形式，然后传输学习知识以识别语义类似的功能。

We extend micro-execution to support different architectures to collect micro-traces for training.
我们扩展了微型执行，以支持不同的架构以收集微量迹线进行培训。
We then develop a novel neural architecture – hierarchical Transformer – to learn approximate execution semantics from micro-traces.
然后，我们开发一个新型神经结构-等级变压器-从微迹中学习近似执行语义。

We implement TREX and evaluate it on 1,472,066 functions from 13 popular software projects and libraries.
我们在13个流行的软件项目和库中实现TREX并评估1,472,066个功能。

TREX outperforms the state-of-the-art tools by 7.8%, 7%, and 14.3%, in cross-architecture, optimization, and obfuscation function matching, respectively, while running up to 8 faster.
TREX分别以7.8％，7％和14.3％的跨架构，优化和混淆函数匹配，优先于最先进的工具，同时运行高达8次。
Moreover, TREX helps uncover 16 vulnerabilities in 180 real-world firmware images with the latest version that are not disclosed by previous studies.
此外，TREX有助于在180个现实世界固件图像中揭示16个漏洞，并使用以前的研究未披露的最新版本。
We release the code and dataset of TREX at https://github.com/CUMLSec/trex.
我们在https://github.com/cumlsec/trex中发布TREX的代码和数据集。

II.
II。
OVERVIEW.
概述。

In this section, we use the real-world functions as motivating examples to describe the challenges of matching semantically similar functions.
在本节中，我们使用现实世界的功能作为激励例子来描述匹配语义类似功能的挑战。
We then overview our approach, focusing on how our pretraining task (masked LM) addresses the challenges.
然后，我们概述了我们的方法，重点是我们的预先训练任务（MassedLM）如何解决挑战。

A. Challenging Cases.
A.挑战性案件。

We use three semantically equivalent but syntactically different function pairs to demonstrate some challenges of learning from only static code.
我们使用三种语义等同物但语法不同的功能对来展示从静态代码中学习的一些挑战。
Figure 2 shows the (partial) assembly code of each function.
图2显示了每个功能的（部分）汇编代码。

Cross-architecture example.
跨架构示例。
Consider the functions in Figure 2a.
考虑图2a中的功能。
Two functions have the same execution semantics as both functions take the lower 12-bit of a register and compare it to 0x80.
两个函数具有相同的执行语义，因为这两个函数都占用寄存器的下部12位并将其与0x80进行比较。
Detecting this similarity requires understanding the approximate execution semantics of and in x86 and lsl/lsr in ARM.
检测此相似度需要了解X86和LSL/LSR中的近似执行语义。
Moreover, it also requires understanding how the values (i.e., 0xfff and 0x14) in the code are manipulated.
此外，它还需要了解如何操纵代码中的值（即0xFFF和0x14）。

However, all existing ML-based approaches [50] only learn on static code without observing each instruction’s real execution effect.
但是，所有现有的基于ML的方法[50]只能在静态代码上学习，而无需观察每个指令的实际执行效果。
Furthermore, to mitigate the potentially prohibitive vocabulary size (i.e., all possible memory addresses), existing approaches replace all register values and memory addresses with an abstract dummy symbol [26], [50].
此外，为了减轻潜在的禁止词汇量（即，所有可能的存储器地址），现有方法用抽象伪符号[26]，[50]替换所有寄存器值和存储器地址。
They thus cannot access the specific byte values to determine inherent similarity.
因此，它们无法访问特定的字节值以确定固有的相似性。

Cross-optimization example.
交叉优化示例。
Now consider two functions in Figure 2b.
现在考虑图2B中的两个功能。
They are semantically equivalent as [ebp+8] and [esp+4] access the same memory location, i.e., the function’s first argument pushed on the stack by the caller.
它们是语义上等同于[EBP+8]和[ESP+4]访问相同的内存位置，即函数由呼叫者推出堆栈上的第一个参数。
To detect such similarity, the model should understand push decreases the stack pointer esp by 4. The model should also notice that mov at line 2 assigns the decremented esp to ebp such that ebp+8 in the upper function equals esp+4 in the lower
要检测到这样的相似性，模型应该理解推送堆栈指针ESP到4.该模型还应注意到第2行的MOV将递减的ESP递减为eBP，使得上函数中的EBP+8等于较低的ESP+4
function.
功能。
However, such dynamic information is not reflected in the static code.
然而，这种动态信息没有反映在静态代码中。

Cross-obfuscation example.
交叉混淆示例。
Figure 2c demonstrates a simple obfuscation by instruction substitution, which essentially replaces eax+1 with eax-(-1).
图2c通过指令替代说明了简单的混淆，基本上用EAX-（-1）替换EAX+1。
Detecting the equivalence requires understanding approximately how arithmetic operations such as xor, sub, and add, executes.
检测等同物需要了解Xor，Sub和Add等算术运算如何执行。
However, static information is not enough to expose such knowledge.
但是，静态信息不足以暴露这些知识。

B. Pretraining Masked LM on Micro-traces.
B.微迹情况下预先曝光蒙版LM。

This section describes how the pretraining task, masked LM, on functions’ micro-traces encourages the model to learn execution semantics.
本节介绍预先绘制的任务，屏蔽LM，函数的微迹情况如何鼓励模型学习执行语义。
Although it remains an open research question to explicitly prove certain knowledge is encoded by such language modeling task [70], we focus on describing the intuition behind the masked LM – why predicting masked codes and values in micro-traces can help address the challenging cases
虽然它仍然是一个开放的研究问题，但明确证明某些知识是由这种语言建模任务进行编码的[70]，我们专注于描述掩码LM后面的直觉-为什么预测微量迹线中的屏蔽代码和值可以帮助解决具有挑战性的情况
in Figure 2.
在图2中。

Masked LM.
蒙面LM。
Recall the operation of masked LM: given a function’s micro-trace (i.e., values and instructions), we mask some random parts and train the model to predict the masked parts using those not masked.
回想蒙镜LM的操作：给定函数的微跟踪（即，值和指令），我们掩盖了一些随机部件并培训模型，以预测使用那些未屏蔽的屏蔽部分。

Note that pretraining with masked LM does not need any manual labeling effort, as it only predicts the masked part in the input micro-traces without any additional labeling effort.
请注意，屏蔽LM的预先预订不需要任何手动标记工作，因为它只预测输入微迹线中的遮蔽部分，而无需任何额外的标记工作。

Therefore, TREX can be trained and further improved with a substantial number of functions found in the wild.
因此，可以通过在野外发现的大量功能进行培训并进一步改善Trex。
The benefit of this is that a certain instruction not micro-executed in one function is highly likely to appear in at least one of the other functions’ micro-traces, supporting TREX to approximate diverse instructions’ execution semantics.
这样做的好处是，在一个功能中没有微型执行的某个指令很可能出现在其他功能的微迹中的至少一个中，支持TREX以近似不同的指令执行语义。

Masking register.
掩蔽寄存器。
Consider the functions in Figure 2c, where they essentially increment the value at stack location [rbp-0x2c] by 1. The upper function directly loads the value to eax, increments by 1, and stores the value in eax back to stack.
考虑图2c中的函数，其中它们基本上将堆栈位置[RBP-0x2C]的值递增1.上函数直接将值加载到EAx，增量为1，并将EAX中的值存储回堆栈。
The lower function, by contrast, takes a convoluted way by first letting ecx to hold the value -1, and decrements eax by ecx, and stores the value in eax back to stack.
相比之下，较低的函数通过首先让ECX保持valy-1，并通过ECX递减EAX，并将EAX的值存储回堆叠。

We mask the eax at line 3 in the upper function.
我们在上部功能中将EAX掩盖。
We find that our pretrained model can correctly predict its name and dynamic value.
我们发现我们的预制模型可以正确预测其名称和动态值。
This implies the model understands the semantics of add and can deduce the value of eax in line 3 after observing the value of eax in line 2 (before the addition takes the effect).
这意味着模型理解添加的语义，并且可以在观察第2行中的EAX的值后在第3行中推断出EAx的值（在添加之前效果之前）。
We also find the model can recover the values of masked ecx in line 4 and eax in line 5, implying the model understands the execution effect of xor and sub.
我们还发现模型可以在第5行中恢复蒙版ECX的值，暗示模型了解XOR和SUB的执行效果。

The understanding of such semantics can significantly improve the robustness in matching similar functions – when finetuned to match similar functions, the model is more likely to learn to attribute the similarity to their similar execution effects, instead of their syntactic similarity.
对这种语义的理解可以显着提高匹配类似函数的鲁棒性-当FineTuned匹配类似的函数时，模型更有可能学会将相似性归因于它们类似的执行效果，而不是它们的语法相似性。

Masking opcode.
屏蔽操作码。
Besides masking the register and its value, we can also mask the opcode of an instruction.
除了屏蔽寄存器及其值外，我们还可以掩盖指令的操作码。
Predicting the opcode requires the model to understand the execution effect of each opcode.
预测操作码需要模型来理解每个操作码的执行效果。
Consider Figure 2b, where we mask mov in line 2 of upper function.
考虑图2B，其中我们在上函数的第2行中掩盖MOV。
We find our pretrained model predicts mov with the largest probability (larger than the other potential candidates such as add, inc, etc.).
我们发现我们的预制模型预测了具有最大概率的MOV（比其他潜在候选者，如Add，Inc等）。

To correctly predict the opcode, the model should have learned several key aspects of the function semantics.
要正确预测操作码，该模型应该学习了函数语义的几个关键方面。
First, according to its context, i.e., the value of ebp at line 3 and esp at line 2, it learns mov is most probable as it assigns the value of esp to ebp.
首先，根据其上下文，即，第3行的EBP值和ESP在第2行，它学习MOV是最可能的，因为它将ESP的值分配给EBP。
Other opcodes are less likely as their execution effect conflicts with the observed resulting register values.
其他操作频率不太可能与观察到的结果寄存器值相冲突。
This also implicitly implies the model learns the approximate execution semantics of mov.
这也隐含地意味着模型了解MOV的近似执行语义。
Second, the model also learns the common calling convention and basic syntax of x86 instructions, e.g., only a subset of opcodes accept two operands (ebp,esp).
其次，该模型还了解X86指令的常见调用约定和基本语法，例如，仅接受两个操作数（EBP，ESP）的Opcodes的子集。
It can thus exclude many syntactically impossible opcodes such as push, jmp, etc.
因此，它可以排除许多句法不可能的操作码，例如推，JMP等。

The model can thus infer ebp (line 3 of upper function) equals to esp.
因此，该模型可以推断出eBP（上函数的第3行）等于ESP。
The model may have also learned push decrements stack pointer esp by 4 bytes, from other masked samples.
该模型还可以从其他掩码样本中学习将推倍堆叠指针ESP递推减少4个字节。
Therefore, when the pretrained model is finetuned to match the two functions, the model is more likely to learn that the semantic equivalence is due to that [ebp+8] in the upper function and [esp+4] in the lower function refer to
因此，当预先训练的模型是FINETUNED以匹配两个功能时，该模型更有可能知道语义等效是由于下函数中的[EBP+8]和较低函数中的[ESP+4]引用
the same address, instead of their similar syntax.
相同的地址，而不是它们类似的语法。

Other masking strategies.
其他掩蔽策略。
Note that we are not constrained by the number or the type of items (ie, register, opcode, etc.) in the instructions to mask, ie, we can mask complete instructions or even a consecutive sequence of instructions, and we can mask dynamic
请注意，我们不会受到掩码的指令中的数量或项目类型或类型（即，寄存器，操作码等）的限制，即，我们可以屏蔽完整的指令甚至连续指令序列，我们可以掩盖动态
values of random instructions' inputoutput.
随机指令输入输出的值。

Moreover, the masking operation dynamically selects random subsets of code blocks and program states at each training iteration and on different training samples.
此外，掩蔽操作在每个训练迭代和不同训练样本上动态地选择代码块和程序状态的随机子集。
As a result, it enables the model to learn the diverse and composite effect of the instruction sequence, essential to detecting similarity between functions with various instructions.
结果，它使模型能够学习指令序列的多样化和复合效果，对于检测具有各种指令之间的功能之间的相似性必不可少。
In this paper, we adopt a completely randomized strategy to choose what part of the micro-trace to mask with a fixed masking percentage (see Section IV-C for details).
在本文中，我们采用完全随机的策略来选择微量痕迹的哪个部分以固定的掩蔽百分比（参见IV-C部分详情）。
However, we envision a quite interesting future work to study a better (but still cheap) strategy to dynamically choose where and how much to mask.
但是，我们设想了一个非常有趣的未来工作，以研究更好（但仍然便宜）战略，以动态选择掩盖的地方和多少。

III.
III。
THREAT MODEL.
威胁模型。

We assume no access to the debug symbols or source while comparing binaries.
在比较二进制文件时，我们假设无法访问调试符号或源。
Indeed, there exist many approaches to reconstruct functions from stripped binaries [4], [6], [24], [62], [72].
实际上，存在许多方法可以从剥离二进制文件[4]，[6]，[24]，[62]，[72]。
Moreover, we assume the binary can be readily disassembled, i.e., it is not packed nor transformed by virtualizationbased obfuscator [73], [74].
此外，我们假设二进制可以容易地拆卸，即，它没有被虚拟化的混淆器[73]，[74]填充也不转换。

Semantic similarity.
语义相似度。
We consider two semantically similar functions as having the same input-output behavior (i.e., given the same input, two functions produce the same output).
我们考虑具有相同输入输出行为的两个语义类似的功能（即，给定相同的输入，两个函数产生相同的输出）。
Similar to previous works [25], [50], [77], we treat functions compiled from the same source as similar, regardless of architectures, compilers, optimizations, and obfuscation transforms.
与以前的作品类似[25]，[50]，[77]，我们将从与相同的源编译的函数和类似的源代码，无论体系结构，编译器，优化和混淆转换如何。

IV.
IV。
METHODOLOGY.
方法。

This section describes TREX’s design specifics, including our micro-tracing semantics, our learning architecture’s details, and pretraining and finetuning workflow.
本节介绍了TREX的设计细节，包括我们的微跟踪语义，我们的学习架构的细节和预先训练和FineTuning工作流程。

A. Micro-tracing Semantics.
A.微跟踪语义。

We implement micro-execution by Godefroid [34] to handle x64, ARM, and MIPS, where the original paper only describes x86 as the use case.
我们通过Godefroid[34]实现微型执行来处理X64，ARM和MIPS，原始纸张仅将X86描述为用例。
In the following, we briefly explain how we micro-execute an individual function binary, highlighting the key algorithms in handling different types of instructions.
在下文中，我们简要解释了我们如何微型执行单独的功能二进制文件，突出显示处理不同类型指令的关键算法。

IR Language.
红外语言。
To abstract away the complexity of different architectures’ assembly syntax, we introduce a low-level intermediate representation (IR) that models function assembly code.
要抽出不同架构的装配语法的复杂性，我们引入了模型函数汇编代码的低级中间表示（IR）。
We only include a subset of the language specifics to illustrate the implementation algorithm.
我们仅包括语言细节的子集来说明实现算法。
Figure 3 shows the grammar of the IR.
图3显示了IR的语法。
Note that the IR here only serves to facilitate the discussion of our micro-tracing implementation.
请注意，IR在此仅用于促进我们微跟踪实现的讨论。

In our implementation, we use real assembly instructions and tokenize them as model’s input (Section IV-B).
在我们的实施中，我们使用真正的装配说明并将其授予为模型的输入（部分IV-B）。

Notably, we denote memory reads and writes by load(e) and store(ev; ea) (ie, store the value expression ev to address expression ea), which generalize from both the loadstore architecture (ie, ARM, MIPS) and register
值得注意的是，我们表示通过加载（e）和存储（ep;ea）（即，将值表达式EV存储到地址表达式EA）的内存读取和写入，这概括了LoadStore架构（即，ARM，MIP）和寄存器
-memory architecture (ie, x86).
-制造架构（即，x86）。
Both operations can take as input e – an expression that can be an explicit hexadecimal number (denoting the address or a constant), a register, or a result of an operation on two registers.
这两个操作都可以作为输入e​​-一种表达式，可以是两个寄存器上的显式十六进制数（表示地址或常数），寄存器或操作的结果。
We use jmp to denote the general jump instruction, which can be both direct or indirect jump (i.e., the expression ea can be a constant c or a register r).
我们使用JMP表示一般跳转指令，它可以是直接或间接跳转（即，表达式EA可以是常数C或寄存器R）。
The jump instruction can also be unconditional or conditional.
跳转指令也可以是无条件的或有条件的。
Therefore, the first parameter in jmp is the conditional expression ec and unconditional jump will set ec to true.
因此，JMP中的第一个参数是条件表达式EC，无条件跳转将EC设置为TRUE。
We represent function invocations and returns by call and ret, where call is parameterized by an expression, which can be an address (direct call) or a register (indirect call).
我们代表函数调用并通过呼叫和返回返回，呼叫由表达式参数化，可以是地址（直接呼叫）或寄存器（间接呼叫）。

Micro-tracing algorithm.
微跟踪算法。
Algorithm 1 outlines the basic steps of micro-tracing a given function f.
算法1概述了给定函数f的微跟踪的基本步骤。
First, it initializes the memory to load the code and the corresponding stack.
首先，它初始化内存以加载代码和相应的堆栈。
It then initializes all registers except the special-purpose register, such as the stack pointer or the program counter.
然后，它初始化除专用寄存器之外的所有寄存器，例如堆栈指针或程序计数器。
Then it starts linearly executing instructions of f.
然后它开始线性执行F的指令。
We map the memory address on-demand if the instruction access the memory (i.e., read/write).
如果指令访问存储器（即，读/写），我们会按需映射内存地址。
If the instruction reads from memory, we further initialize a random value in the specific memory addresses.
如果指令从内存中读取，则进一步初始化特定内存地址中的随机值。
For call/jump instructions, we first examine the target address and skip the invalid jump/call, known as “forced execution” [63].
对于呼叫/跳转指令，我们首先检查目标地址并跳过无效的跳转/呼叫，称为“强制执行”[63]。
By skipping unreachable jumps and calls, it can keep executing the function till the end of the function and exposes more behaviors, e.g., skipping potential input check exceptions.
通过跳过无法访问的跳转和呼叫，它可以继续执行功能直到函数的末尾并暴露更多行为，例如，跳过潜在输入检查异常。
Since the nop instructions can serve as padding between instructions within a function, we simply skip nop.
由于NOP指令可以作为函数内的指令之间的填充，因此我们只需跳过NOP。
We terminate the micro-tracing when it finishes executing all instructions, reaches ret, or times out.
当它完成执行所有指令时，我们终止微跟踪，达到RET或超时。
Figure 13 and 14 demonstrate sample micro-traces of real-world functions.
图13和14展示了现实世界的样本微迹。

B. Input Representation.
B.输入表示。

Formally, given a function f (i.e., assembly code) and its micro-trace t (by micro-executing f), we prepare the model input x, consisting of 5 types of token sequence with the same size n.
正式地，给定函数f（即，汇编代码）及其微跟踪t（通过微跟踪t），我们准备模型输入x，由具有相同大小的5种类型的令牌序列组成。
Figure 4 shows the model input example and how they are masked and processed by the hierarchical Transformer to predict the corresponding output as a pretraining task.
图4显示了模型输入示例以及它们是由分层变换器屏蔽和处理的模型输入示例，以将相应的输出预测为预先训练任务。

Micro-trace code sequence.
微跟踪码序列。
The first sequence xf is the assembly code sequence: xf = fmov;
第一个序列XF是汇编代码序列：XF=FMOV;
eax;+;
eax;+;
:::gn, generated by tokenizing the assembly instructions in the micro-trace.
:::GN，通过授权微跟踪中的装配说明生成。
We treat all symbols appear in the assembly instructions as tokens.
我们将所有符号视为令牌的装配说明中显示所有符号。

Such a tokenization aims to preserve the critical hint of the syntax and semantics of the assembly instructions.
这种令牌化旨在保留大量说明的语法和语义的临界提示。
For example, we consider even punctuation to be one of the tokens, eg, “,”, “[”, “]”, as “,” implies the token before and after it as destination and source of mov (in Intel syntax)
例如，我们认为即使是标点符号也是一个令牌，例如“，”，“[”，“，”，“，”，“”，“在它之前和之后暗示的令牌作为目标和源（在英特尔语法中）
, respectively, and “[” and “]” denote taking the address of the operands reside in between them.
分别和“[”和“]”表示，拍摄操作数的地址驻留在它们之间。

We take special treatment of numerical values appear in the assembly code.
我们采取特殊处理数值出现在汇编代码中。
Treating numerical values as regular text tokens can incur prohibitively large vocabulary size, e.g., 232 number of possibilities on 32-bit architectures.
将数值视为常规文本令牌可能会产生过大的词汇量，例如32位架构上的232个可能性。
To avoid this problem, we move all numeric values to the micro-trace value sequence (that will be learned by an additional neural network as detailed in the following) and replace them with a special token num (eg, last token of input in Figure
为了避免这个问题，我们将所有数值移动到微跟踪值序列（将通过以下内容详述的附加神经网络学习），并用特殊的令牌Num替换它们（例如，图中输入的最后令牌
4).
4）。
With all these preprocessing steps, the vocabulary size of xf across all architectures is 3,300.
通过所有这些预处理步骤，所有架构的XF的词汇量为3,300。

Micro-trace value sequence.
微量痕量值序列。
The second sequence xt is the micro-trace value sequence, where each token in xt is the dynamic value from micro-tracing the corresponding code.
第二个序列XT是微跟踪值序列，其中XT中的每个令牌是从微跟踪相应代码的动态值。
As discussed in Section II, we keep explicit values (instead of a dummy value used by existing approaches) in xt.
如第II部分所讨论的，我们在XT中保留显式值（而不是现有方法使用的虚拟值）。
Notably, we use the dynamic value for each token (e.g., register) in an instruction before it is executed.
值得注意的是，我们在执行之前的指令中使用每个令牌（例如，寄存器）的动态值。
For example, in mov eax,0x8;
例如，在MOVEAX，0x8;
mov eax,0x3, the dynamic value of the second eax is 0x8, as we take the value of eax before mov eax,0x3 is executed.
MOVEAX，0x3，第二EAX的动态值为0x8，因为我们在MOVEAX之前取得EAX的值，执行0x3。
For code token without dynamic value, e.g., mov, we use dummy values (see below).
对于没有动态值的代码令牌，例如，MOV，我们使用虚拟值（见下文）。

Position sequences.
位置序列。
The position of each code and value token is critical for inferring binary semantics.
每个代码和值令牌的位置对于推断二进制语义至关重要。
Unlike natural language, where swapping two words can roughly preserve the same semantic meaning, swapping two operands can significantly change the instructions.
与自然语言不同，在交换两个单词可以大致保持相同的语义含义，交换两个操作数可以显着改变指令。
To encode the inductive bias of position into our model, we introduce instruction position sequence xc and opcode/operand position sequence xo to represent the relative positions between the instructions and within each instruction.
要将位置的归纳偏差进行编码到我们的模型中，我们介绍了指令位置序列XC和操作码/操作数位置序列XO，以表示指令和每个指令内的相对位置。
As shown in Figure 4, xc is a sequence of integers encoding the position of each instruction.
如图4所示，XC是编码每个指令位置的整数序列。

All opcodes/operands within a single instruction share the same value.
单个指令中的所有操作码/操作数共享相同的值。
xo is a sequence of integers encoding the position of each opcode and operands within a single instruction.
XO是一系列整数，编码每个操作码和操作数在单个指令中的位置。

Architecture sequence.
架构序列。
Finally, we feed the model with an extra sequence xa, describing the input binary’s instruction set architecture.
最后，我们用额外的序列XA馈送模型，描述了输入二进制指令集架构。
The vocabulary of xa consists of 4 architectures: xa = fx86, x64, ARM, MIPSgn.
XA的词汇包括4个架构：XA=FX86，X64，ARM，MIPSGN。
This setting helps the model to distinguish between the syntax of different architecture.
此设置有助于模型区分不同架构的语法。

Encoding numeric values.
编码数值。
As mentioned above, treating concrete values as independent tokens can lead to prohibitively large vocabulary size.
如上所述，将混凝土值视为独立的令牌，可以导致过大的词汇量。
We design a hierarchical input encoding scheme to address this challenge.
我们设计一个分层输入编码方案来解决这一挑战。
Specifically, let xti denote the i-th value in xt.
具体来说，让XTI表示XT中的第i值。
We represent xti as an (padded) 8-byte fixed-length byte sequence xti =f0x00, ..., 0xffg8 ordered in Big-Endian.
我们将XTI代表为（填充）8字节的固定长度字节序列XTI=F0x00，...，0xFFG8在Big-Endian中排序。
We then feed xti to a 2-layer bidirectional LSTM (bi-LSTM) and take its last hidden cell’s embedding as the value representation ti = bi-LSTM(xti ).
然后，我们将XTI馈送到2层双向LSTM（Bi-LSTM），并将其最后一个隐藏的单元格嵌入为值表示Ti=Bi-LSTM（XTI）。
Here ti denotes the output of applying the embedding to xti .
这里TI表示将嵌入到XTI应用于XTI的输出。
To make the micro-trace code tokens without dynamic values (e.g., opcode) align with the byte sequence, we use a dummy sequence (##) with the same length.
为了使微跟踪代码令牌没有动态值（例如，操作码）与字节序列对齐，我们使用具有相同长度的虚拟序列（##）。
Figure 4 (right-hand side) illustrates how bi-LSTM takes the byte sequence and computes the embedding.
图4（右侧）示出了双LSTM如何采用字节序列并计算嵌入。

Such a design significantly reduces the vocabulary size as now we have only 256 possible byte values to encode.
这样的设计显着降低了现在的词汇量，我们只有256个可能的字节值来编码。
Moreover, bi-LSTM encodes the potential dependencies between high and low bytes within a single value.
此外，Bi-LSTM在单个值内对高低字节之间的潜在依赖性进行编码。
This setting thus supports learning better relationships between different dynamic values (e.g., memory region and offset) as opposed to treating all values as dummy tokens [71].
因此，该设置支持在不同动态值（例如，存储区域和偏移）之间的学习更好的关系，而不是将所有值视为虚拟令牌[71]。

                                                                                                                                                                       paper/__pycache__/                                                                                  0000775 0001750 0001750 00000000000 14116010257 012512  5                                                                                                    ustar   mqa                             mqa                                                                                                                                                                                                                    paper/__pycache__/GoogleTrans.cpython-38.pyc                                                        0000664 0001750 0001750 00000006403 14116010257 017371  0                                                                                                    ustar   mqa                             mqa                                                                                                                                                                                                                    U
    ?!7a/  ?                   @   s?   d dl Zd dlZd dlZd dlZd dlZd dlZd dlZeje_	G dd? de
?Zedkr?dZe? jedd?\ZZZZeeeee? dS )?    Nc                   @   s.   e Zd Zdd? Zdd? Zdd? Zddd	?Zd
S )?GoogleTransc                 C   s?   d| _ d| _ddddddd	?| _d
dddddddddddddg
ddddddd?| _tdddd ??}t?|?? ?| _W 5 Q R X d S )!Nz.https://translate.google.cn/translate_a/singlez434674.96463358z*/*zzh-CN,zh;q=0.9z?NID=188=M1p_rBfweeI_Z02d1MOSQ5abYsPfZogDrFjKwIUbmAr584bc9GBZkfDwKQ80cQCQC34zwD4ZYHFMUf4F59aDQLSc79_LcmsAihnW0Rsb1MjlzLNElWihv-8KByeDBblR2V1kjTSC8KnVMe32PNSJBQbvBKvgl4CTfzvaIEgkqss?https://translate.google.cn/zsMozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36zLCJK2yQEIpLbJAQjEtskBCKmdygEIqKPKAQi5pcoBCLGnygEI4qjKAQjxqcoBCJetygEIza3KAQ==)Zacceptzaccept-languageZcookieZrefererz
user-agentzx-client-dataZwebappZautoZvi?zh-CNZatZbdZexZldZmdZqcaZrwZrmZss?t?2?0?1? )ZclientZsl?tlZhlZdtZotfZsselZtselZkc?tk?qztoken.js?r?utf-8)?encoding)	?url?TKK?header?data?open?execjs?compile?read?js_fun)?self?f? r   ?#/home/mqa/misc/paper/GoogleTrans.py?__init__   s.    ?
?zGoogleTrans.__init__c                 C   sB   d}t jj|| jd?}t j?|??? ?d?}t?d|?d | _	d S )Nr   ?r   Zheadersr   ztkk:'([0-9]+\.[0-9]+)'r   )
?urllib?request?Requestr   ?urlopenr   ?decode?reZfindallr   )r   r   ?reqZpage_sourcer   r   r   ?
update_TKK2   s    zGoogleTrans.update_TKKc                 C   sn   | j d }| jD ]L}t| j| t?rB|d d?| j| ? d }q|| d | j|  d }q|d d? }|S )N??zdt=z&dt=?&?=?????)r   r   ?
isinstance?list?join)r   ?base?keyr   r   r   ?construct_url9   s    

zGoogleTrans.construct_urlr	   c                    s?   dd? ?t j?|?| jd< | j?d|| j?| jd< || jd< | ?? }t jj	|| j
d?}t?t j?|??? ?d??? d	?? ?fd
d?tt? d ??D ??}? d d d }? d }||||fS )Nc                 S   s   | ? dd?? dd?? dd?S )N?r	   ?
? )?replace)?strr   r   r   ?rmspD   s    zGoogleTrans.query.<locals>.rmspr   Zwor   r
   r   r   r2   c                    sL   g | ]D}? d  | d  dk	r? d  | d ? ? d ?? d  | d  ? ?qS )r   N?   r2   )?strip)?.0?i?Zresponser6   r   r   ?
<listcomp>M   s      z%GoogleTrans.query.<locals>.<listcomp>r   r7   ?   )r   ZparseZquoter   r   Zcallr   r0   r    r!   r   ?json?loadsr"   r   r#   r-   ?range?len)r   r   ?lang_tor   r%   ?
targetText?originalText?originalLanguageCoder   r;   r   ?queryC   s    
&zGoogleTrans.queryN)r	   )?__name__?
__module__?__qualname__r   r&   r0   rF   r   r   r   r   r      s   "
r   ?__main__zHello worldr   )rB   )Zurllib.requestr   Zurllib.parser>   r   r$   Zssl?textwrapZ_create_unverified_contextZ_create_default_https_context?objectr   rG   ?textrF   rD   rE   rC   ZtargetLanguageCode?printr   r   r   r   ?<module>   s   F                                                                                                                                                                                                                                                             paper/token.js                                                                                      0000775 0001750 0001750 00000002311 14115602554 011766  0                                                                                                    ustar   mqa                             mqa                                                                                                                                                                                                                    var uo = function (a, b) {
    for (var c = 0; c < b.length - 2; c += 3) {
        var d = b.charAt(c + 2);
        d = "a" <= d ? d.charCodeAt(0) - 87 : Number(d);
        d = "+" == b.charAt(c + 1) ? a >>> d : a << d;
        a = "+" == b.charAt(c) ? a + d & 4294967295 : a ^ d
    }
    return a
},

wo = function (a, tkk) { // 需要在调用函数时传入window['TKK']的值
	var d = tkk.split(".");
    var b = Number(d[0]); 
    for (var e = [], f = 0, g = 0; g < a.length; g++) { 
        var h = a.charCodeAt(g); 
        128 > h ? e[f++] = h : 
            (2048 > h ? e[f++] = h >> 6 | 192 : 
                    (55296 == (h & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (h = 65536 + ((h & 1023) << 10) + (a.charCodeAt(++g) & 1023), e[f++] = h >> 18 | 240, e[f++] = h >> 12 & 63 | 128) :
                        e[f++] = h >> 12 | 224, e[f++] = h >> 6 & 63 | 128), e[f++] = h & 63 | 128)
    }
    a = b; 
    for (f = 0; f < e.length; f++)
        a += e[f],
        a = uo(a, "+-a^+6"); 
    a = uo(a, "+-3^+b+-f");
    a ^= Number(d[1]) || 0; 
    0 > a && (a = (a & 2147483647) + 2147483648); 
    a %= 1E6;
    return (a.toString() + "." + (a ^ b))
};                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       