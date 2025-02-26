# Pass编写

## 测试用例

```
├── build
├── CMakeLists.txt
├── include
└── src
    └── hello.cpp
```

### hello.cpp

```cpp
#include "llvm/IR/PassManager.h"  // 引入新的 Pass 管理相关头文件
#include "llvm/IR/Function.h"  // 添加这行，引入包含 Function 完整定义的头文件
#include "llvm/Passes/PassPlugin.h"  // 引入新的 Pass 插件相关头文件
#include "llvm/Passes/PassBuilder.h"
using namespace llvm;

namespace {
    // 继承自 PassInfoMixin 以及 FunctionAnalysisManagerMixin（如果需要分析函数相关信息的话）等新基类
    class Hello : public PassInfoMixin<Hello> {
    public:
        // 实现 run 方法来定义 Pass 的核心执行逻辑，替代原来的 runOnFunction
        PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM) {
            errs() << "Hello: ";
            errs().write_escaped(F.getName()) << '\n';
            // 根据实际对函数分析或修改的情况返回合适的 PreservedAnalyses 值，这里简单返回所有分析都未被修改的标识
            return PreservedAnalyses::all();
        }
        // 静态方法用于提供 Pass 的名称等元信息，类似旧版本里的 ID 等概念
        static bool isRequired() { return true; }
        static StringRef getPassName() { return "Hello world Pass"; }
    };
}

// 注册函数，将 Hello Pass 注册到对应的 Pass 注册器中
llvm::PassPluginLibraryInfo getHelloPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION, "hello", LLVM_VERSION_STRING,
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                   ArrayRef<PassBuilder::PipelineElement>) {  // 修改此处，将 Rourke 更正为 PipelineElement
                    if (Name == "hello") {
                        FPM.addPass(Hello());
                        return true;
                    }
                    return false;
                });
        }
    };
}

// 定义插件入口点函数，这是 LLVM 插件机制要求的
extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return getHelloPluginInfo();
}
```

### CMakeLists.txt

```
cmake_minimum_required(VERSION 3.13)
project(LLVMHelloPass)

find_package(LLVM REQUIRED CONFIG)

# 设置编译选项等，根据实际 LLVM 版本等情况调整
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-rtti")

# 添加源文件到项目
add_library(LLVMHelloPass SHARED
    src/hello.cpp
)


# 设置安装相关路径等（可选，根据需求添加）
install(TARGETS LLVMHelloPass
    LIBRARY DESTINATION lib
)
```

### command

```shell
# 编译
cd build
cmake ..
make
# 使用
opt -load-pass-plugin=./build/libLLVMHelloPass.so -passes=hello test.ll -o test.bc
clang test.bc -o test
```

## OLLVM

为了学习 OLLVM 的混淆原理，并且方便自己写混淆，这里将 OLLVM 的代码移到了 LLVM 20.0 上，且改写了新版本的 API。

### Substitution

```cpp
#include "llvm/Pass.h"
#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Instructions.h"
#include "llvm/ADT/Statistic.h"
#include "llvm/Transforms/IPO.h"
#include "llvm/IR/Module.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Transforms/Utils.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"
using namespace llvm;

#define NUMBER_ADD_SUBST 4
#define NUMBER_SUB_SUBST 3
#define NUMBER_AND_SUBST 2
#define NUMBER_OR_SUBST 2
#define NUMBER_XOR_SUBST 2


namespace {
    // 指定函数进行混淆
    cl::list<std::string> FunctionsToObfuscate("funcs", cl::desc("Specify function names to obfuscate"), cl::CommaSeparated);
    // 指定混淆次数
    cl::opt<int> ObfTimes(
        "sub_loop", 
        cl::desc("Choose how many time the -sub pass loops on a function"), 
        cl::value_desc("number of times"), 
        cl::init(1), 
        cl::Optional
    );

    class Substitution : public PassInfoMixin<Substitution> {
    public:
        static bool isRequired() { return true; }
        static StringRef getPassName() { return "Substitution Pass"; }
        
        void (Substitution::*funcAdd[NUMBER_ADD_SUBST])(BinaryOperator *bo);
        void (Substitution::*funcSub[NUMBER_SUB_SUBST])(BinaryOperator *bo);
        void (Substitution::*funcAnd[NUMBER_AND_SUBST])(BinaryOperator *bo);
        void (Substitution::*funcOr[NUMBER_OR_SUBST])(BinaryOperator *bo);
        void (Substitution::*funcXor[NUMBER_XOR_SUBST])(BinaryOperator *bo);

        Substitution() {
            srand(time(nullptr));
            funcAdd[0] = &Substitution::addNeg;
            funcAdd[1] = &Substitution::addDoubleNeg;
            funcAdd[2] = &Substitution::addRand;
            funcAdd[3] = &Substitution::addRand2;
            funcSub[0] = &Substitution::subNeg;
            funcSub[1] = &Substitution::subRand;
            funcSub[2] = &Substitution::subRand2;
            funcAnd[0] = &Substitution::andSubstitution;
            funcAnd[1] = &Substitution::andSubstitutionRand;
            funcOr[0] = &Substitution::orSubstitution;
            funcOr[1] = &Substitution::orSubstitutionRand;
            funcXor[0] = &Substitution::xorSubstitution;
            funcXor[1] = &Substitution::xorSubstitutionRand;
        }

        PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM) {
            if (ObfTimes <= 0) {
                errs() << "Substitution application number -sub_loop=x must be x > 0\n";
                return PreservedAnalyses::all();
            }
            if (std::find(FunctionsToObfuscate.begin(), FunctionsToObfuscate.end(), F.getName()) == FunctionsToObfuscate.end()) {
                return PreservedAnalyses::all();
            }
            substitute(&F);
            return PreservedAnalyses::all();
        }
        
        bool substitute(Function *f) {
            Function *tmp = f;
            int times = ObfTimes;
            do {
                for (Function::iterator bb = tmp->begin(); bb != tmp->end(); ++bb) {
                    for (BasicBlock::iterator inst = bb->begin(); inst != bb->end(); ++inst) {
                        if (inst->isBinaryOp()) {
                            switch (inst->getOpcode()) {
                                case BinaryOperator::Add:{
                                    (this->*funcAdd[rand() % NUMBER_ADD_SUBST])(cast<BinaryOperator>(inst));
                                    break;
                                }
                                case BinaryOperator::Sub:{
                                    (this->*funcSub[rand() % NUMBER_SUB_SUBST])(cast<BinaryOperator>(inst));
                                    break;
                                }
                                case BinaryOperator::And:{
                                    (this->*funcAnd[rand() % NUMBER_AND_SUBST])(cast<BinaryOperator>(inst));
                                    break;
                                }
                                case BinaryOperator::Or:{
                                    (this->*funcOr[rand() % NUMBER_OR_SUBST])(cast<BinaryOperator>(inst));
                                    break;
                                }
                                case BinaryOperator::Xor:{
                                    (this->*funcXor[rand() % NUMBER_XOR_SUBST])(cast<BinaryOperator>(inst));
                                    break;
                                }
                                default:
                                    break;
                            }
                        }
                    }
                }
            } while (--times > 0);
            return true;
        }

        // a = b + c -> a = b - (-c)
        void addNeg(BinaryOperator *bo) {
            if (bo->getOpcode() != Instruction::Add) return;
            Value *lhs = bo->getOperand(0);
            Value *rhs = bo->getOperand(1);
            BasicBlock::iterator insertPos(bo);
            BinaryOperator *negRhs = BinaryOperator::CreateNeg(rhs);
            negRhs->insertBefore(bo);
            BinaryOperator *newOp = BinaryOperator::Create(Instruction::Sub, lhs, negRhs);
            newOp->insertBefore(bo);
            bo->replaceAllUsesWith(newOp);
        }

        // a = b + c -> a = -(-b + -c)
        void addDoubleNeg(BinaryOperator *bo) {
            if (bo->getOpcode() != Instruction::Add) return;
            Value *lhs = bo->getOperand(0);
            Value *rhs = bo->getOperand(1);
            BasicBlock::iterator insertPos(bo);
            BinaryOperator *negLhs = BinaryOperator::CreateNeg(lhs);
            negLhs->insertBefore(bo);
            BinaryOperator *negRhs = BinaryOperator::CreateNeg(rhs);
            negRhs->insertBefore(bo);
            BinaryOperator *newOp = BinaryOperator::Create(Instruction::Add, negLhs, negRhs);
            newOp->insertBefore(bo);
            BinaryOperator *finalOp = BinaryOperator::CreateNeg(newOp);
            finalOp->insertBefore(bo);
            bo->replaceAllUsesWith(finalOp);
        }

        // a = b + c -> a = b + r; a = a + c; a = a - r
        void addRand(BinaryOperator *bo) {
            if (bo->getOpcode() != Instruction::Add) return;
            Value *lhs = bo->getOperand(0);
            Value *rhs = bo->getOperand(1);
            BasicBlock::iterator insertPos(bo);
            Constant *rand_num = ConstantInt::get(bo->getType(), rand());
            BinaryOperator *newOp = BinaryOperator::Create(Instruction::Add, lhs, rand_num);
            newOp->insertBefore(bo);
            BinaryOperator *newOp2 = BinaryOperator::Create(Instruction::Add, newOp, rhs);
            newOp2->insertBefore(bo);
            BinaryOperator *finalOp = BinaryOperator::Create(Instruction::Sub, newOp2, rand_num);
            finalOp->insertBefore(bo);
            bo->replaceAllUsesWith(finalOp);
        }

        // a = b + c -> a = b - r; a = a + c; a = a + r
        void addRand2(BinaryOperator *bo) {
            if (bo->getOpcode() != Instruction::Add) return;
            Value *lhs = bo->getOperand(0);
            Value *rhs = bo->getOperand(1);
            BasicBlock::iterator insertPos(bo);
            Constant *rand_num = ConstantInt::get(bo->getType(), rand());
            BinaryOperator *newOp = BinaryOperator::Create(Instruction::Sub, lhs, rand_num);
            newOp->insertBefore(bo);
            BinaryOperator *newOp2 = BinaryOperator::Create(Instruction::Add, newOp, rhs);
            newOp2->insertBefore(bo);
            BinaryOperator *finalOp = BinaryOperator::Create(Instruction::Add, newOp2, rand_num);
            finalOp->insertBefore(bo);
            bo->replaceAllUsesWith(finalOp);
        }
    
        // a = b - c -> a = b + (-c)
        void subNeg(BinaryOperator *bo) {
            if (bo->getOpcode() != Instruction::Sub) return;
            Value *lhs = bo->getOperand(0);
            Value *rhs = bo->getOperand(1);
            BasicBlock::iterator insertPos(bo);
            BinaryOperator *negRhs = BinaryOperator::CreateNeg(rhs);
            negRhs->insertBefore(bo);
            BinaryOperator *newOp = BinaryOperator::Create(Instruction::Add, lhs, negRhs);
            newOp->insertBefore(bo);
            bo->replaceAllUsesWith(newOp);
        }

        // a = b - c -> a = b + r; a = a - c; a = a - r
        void subRand(BinaryOperator *bo) {
            if (bo->getOpcode() != Instruction::Sub) return;
            Value *lhs = bo->getOperand(0);
            Value *rhs = bo->getOperand(1);
            BasicBlock::iterator insertPos(bo);
            Constant *rand_num = ConstantInt::get(bo->getType(), rand());
            BinaryOperator *newOp = BinaryOperator::Create(Instruction::Add, lhs, rand_num);
            newOp->insertBefore(bo);
            BinaryOperator *newOp2 = BinaryOperator::Create(Instruction::Sub, newOp, rhs);
            newOp2->insertBefore(bo);
            BinaryOperator *finalOp = BinaryOperator::Create(Instruction::Sub, newOp2, rand_num);
            finalOp->insertBefore(bo);
            bo->replaceAllUsesWith(finalOp);
        }
    
        // a = b - c -> a = b - r; a = a - c; a = a + r
        void subRand2(BinaryOperator *bo) {
            if (bo->getOpcode() != Instruction::Sub) return;
            Value *lhs = bo->getOperand(0);
            Value *rhs = bo->getOperand(1);
            BasicBlock::iterator insertPos(bo);
            Constant *rand_num = ConstantInt::get(bo->getType(), rand());
            BinaryOperator *newOp = BinaryOperator::Create(Instruction::Sub, lhs, rand_num);
            newOp->insertBefore(bo);
            BinaryOperator *newOp2 = BinaryOperator::Create(Instruction::Sub, newOp, rhs);
            newOp2->insertBefore(bo);
            BinaryOperator *finalOp = BinaryOperator::Create(Instruction::Add, newOp2, rand_num);
            finalOp->insertBefore(bo);
            bo->replaceAllUsesWith(finalOp);
        }

        // a = a & b -> a = (b ^ ~c) & b
        void andSubstitution(BinaryOperator *bo) {
            if (bo->getOpcode() != Instruction::And) return;
            Value *lhs = bo->getOperand(0);
            Value *rhs = bo->getOperand(1);
            BasicBlock::iterator insertPos(bo);
            BinaryOperator *notRhs = BinaryOperator::CreateNot(rhs);
            notRhs->insertBefore(bo);
            BinaryOperator *xorOp = BinaryOperator::Create(Instruction::Xor, lhs, notRhs);
            xorOp->insertBefore(bo);
            BinaryOperator *newOp = BinaryOperator::Create(Instruction::And, xorOp, lhs);
            newOp->insertBefore(bo);
            bo->replaceAllUsesWith(newOp);
        }

        //  a = b && c -> a = !(!b | !c) && (r | !r)
        void andSubstitutionRand(BinaryOperator *bo) {
            if (bo->getOpcode() != Instruction::And) return;
            Value *lhs = bo->getOperand(0);
            Value *rhs = bo->getOperand(1);
            Constant *rand_num = ConstantInt::get(bo->getType(), rand());
            BasicBlock::iterator insertPos(bo);
            BinaryOperator *notLhs = BinaryOperator::CreateNot(lhs);
            notLhs->insertBefore(bo);
            BinaryOperator *notRhs = BinaryOperator::CreateNot(rhs);
            notRhs->insertBefore(bo);
            BinaryOperator *notRand = BinaryOperator::CreateNot(rand_num);
            notRand->insertBefore(bo);
            // !b | !c
            BinaryOperator *orOp1 = BinaryOperator::Create(Instruction::Or, notLhs, notRhs);
            orOp1->insertBefore(bo);
            // r | !r
            BinaryOperator *orRand = BinaryOperator::Create(Instruction::Or, rand_num, notRand);
            orRand->insertBefore(bo);
            // !(!b | !c)
            BinaryOperator *not_orOp1 = BinaryOperator::CreateNot(orOp1);
            not_orOp1->insertBefore(bo);
            // !(!b | !c) && (r | !r)
            BinaryOperator *newOp = BinaryOperator::Create(Instruction::And, not_orOp1, orRand);
            newOp->insertBefore(bo);
            bo->replaceAllUsesWith(newOp);
        }

        // a = b | c -> a = (b & c) | (b ^ c)
        void orSubstitution(BinaryOperator *bo) {
            if (bo->getOpcode() != Instruction::Or) return;
            Value *lhs = bo->getOperand(0);
            Value *rhs = bo->getOperand(1);
            BasicBlock::iterator insertPos(bo);
            BinaryOperator *andOp = BinaryOperator::Create(Instruction::And, lhs, rhs);
            andOp->insertBefore(bo);
            BinaryOperator *xorOp = BinaryOperator::Create(Instruction::Xor, lhs, rhs);
            xorOp->insertBefore(bo);
            BinaryOperator *newOp = BinaryOperator::Create(Instruction::Or, andOp, xorOp);
            newOp->insertBefore(bo);
            bo->replaceAllUsesWith(newOp);
        }

        // a = b | c => [(!a && r) || (a && !r) ^ (!b && r) ||(b && !r) ] || [!(!a || !b) && (r || !r)]
        void orSubstitutionRand(BinaryOperator *bo) {
            if (bo->getOpcode() != Instruction::Or) return;
            Value *lhs = bo->getOperand(0);
            Value *rhs = bo->getOperand(1);
            Constant *rand_num = ConstantInt::get(bo->getType(), rand());
            BasicBlock::iterator insertPos(bo);
            BinaryOperator *op = BinaryOperator::CreateNot(lhs);
            op->insertBefore(bo);
            BinaryOperator *op1 = BinaryOperator::CreateNot(rhs);
            op1->insertBefore(bo);
            BinaryOperator *op2 = BinaryOperator::CreateNot(rand_num);
            op2->insertBefore(bo);
            // !b & r
            BinaryOperator *op3 = BinaryOperator::Create(Instruction::And, op, rand_num);
            op3->insertBefore(bo);
            // b & !r
            BinaryOperator *op4 = BinaryOperator::Create(Instruction::And, lhs, op2);
            op4->insertBefore(bo);
            // !c & r
            BinaryOperator *op5 = BinaryOperator::Create(Instruction::And, op1, rand_num);
            op5->insertBefore(bo);
            // c & !r
            BinaryOperator *op6 = BinaryOperator::Create(Instruction::And, rhs, op2);
            op6->insertBefore(bo);
            // (!b & r) | (b & !r)
            op3 = BinaryOperator::Create(Instruction::Or, op3, op4);
            op3->insertBefore(bo);
            // (!c & r) | (c & !r)
            op4 = BinaryOperator::Create(Instruction::Or, op5, op6);
            op4->insertBefore(bo);
            // (!b & r) | (b & !r) ^ (!c & r) | (c & !r)
            op5 = BinaryOperator::Create(Instruction::Xor, op3, op4);
            op5->insertBefore(bo);
            // !b | !c
            op3 = BinaryOperator::Create(Instruction::Or, op, op1);
            op3->insertBefore(bo);
            // !(!b | !c)
            op3 = BinaryOperator::CreateNot(op3);
            op3->insertBefore(bo);
            // r | !r
            op4 = BinaryOperator::Create(Instruction::Or, rand_num, op2);
            op4->insertBefore(bo);
            // !(!b | !c) & (r | !r)
            op4 = BinaryOperator::Create(Instruction::And, op3, op4);
            op4->insertBefore(bo);
            // [(!b & r) | (b & !r) ^ (!c & r) | (c & !r)] | [!(!b | !c) & (r | !r)]
            op = BinaryOperator::Create(Instruction::Or, op5, op4);
            op->insertBefore(bo);
            bo->replaceAllUsesWith(op);
        }

        // a = b ^ c -> a = (!b & c) | (b & !c)
        void xorSubstitution(BinaryOperator *bo) {
            if (bo->getOpcode() != Instruction::Xor) return;
            Value *lhs = bo->getOperand(0);
            Value *rhs = bo->getOperand(1);
            BasicBlock::iterator insertPos(bo);
            BinaryOperator *notLhs = BinaryOperator::CreateNot(lhs);
            notLhs->insertBefore(bo);
            BinaryOperator *notRhs = BinaryOperator::CreateNot(rhs);
            notRhs->insertBefore(bo);
            // !b & c
            BinaryOperator *andOp1 = BinaryOperator::Create(Instruction::And, notLhs, rhs);
            andOp1->insertBefore(bo);
            // b & !c
            BinaryOperator *andOp2 = BinaryOperator::Create(Instruction::And, lhs, notRhs);
            andOp2->insertBefore(bo);
            // (!b & c) | (b & !c)
            BinaryOperator *orOp = BinaryOperator::Create(Instruction::Or, andOp1, andOp2);
            orOp->insertBefore(bo);
            bo->replaceAllUsesWith(orOp);
        }

        //  a = b ^ c -> a = (!b & r) | (b & !r) ^ (!c & r) | (c & !r)
        void xorSubstitutionRand(BinaryOperator *bo) {
            if (bo->getOpcode() != Instruction::Xor) return;
            Value *lhs = bo->getOperand(0);
            Value *rhs = bo->getOperand(1);
            Constant *rand_num = ConstantInt::get(bo->getType(), rand());
            BasicBlock::iterator insertPos(bo);
            // !b
            BinaryOperator *notLhs = BinaryOperator::CreateNot(lhs);
            notLhs->insertBefore(bo);
            // !c
            BinaryOperator *notRhs = BinaryOperator::CreateNot(rhs);
            notRhs->insertBefore(bo);
            // !r
            BinaryOperator *notRand = BinaryOperator::CreateNot(rand_num);
            notRand->insertBefore(bo);
            // !b && r
            BinaryOperator *op0 = BinaryOperator::Create(Instruction::And, notLhs, rand_num);
            op0->insertBefore(bo);
            // b && !r
            BinaryOperator *op1 = BinaryOperator::Create(Instruction::And, lhs, notRand);
            op1->insertBefore(bo);
            // !c && r
            BinaryOperator *op2 = BinaryOperator::Create(Instruction::And, notRhs, rand_num);
            op2->insertBefore(bo);
            // c && !r
            BinaryOperator *op3 = BinaryOperator::Create(Instruction::And, rhs, notRand);
            op3->insertBefore(bo);
            // (!b & r) | (b & !r)
            op0 = BinaryOperator::Create(Instruction::Or, op0, op1);
            op0->insertBefore(bo);
            // (!c & r) | (c & !r)
            op1 = BinaryOperator::Create(Instruction::Or, op2, op3);
            op1->insertBefore(bo);
            // (!b & r) | (b & !r) ^ (!c & r) | (c & !r)
            op0 = BinaryOperator::Create(Instruction::Xor, op0, op1);
            op0->insertBefore(bo);
            bo->replaceAllUsesWith(op0);
        }
    };
}

llvm::PassPluginLibraryInfo getSubstitutionPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION, "substitution", LLVM_VERSION_STRING,
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "substitution") {
                        FPM.addPass(Substitution());
                        return true;
                    }
                    return false;
                });
        }
    };
}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return getSubstitutionPluginInfo();
}
```

### Flattening

#### 一些问题

前面理解控制流平坦化时，忽略了个细节（太粗心了），导致自己移植到 LLVM20 时，出现了错误。

在这里讲解一下，以作记录。

原来 OLLVM 里使用的~~随机数~~（严格来说不叫随机数，是类似 ID 这种独一无二的东西）的生成方式如下：

```c
unsigned CryptoUtils::scramble32(const unsigned in, const char key[16]) {
    assert(key != NULL && "CryptoUtils::scramble key=NULL");

    unsigned tmpA, tmpB;

    // Orr, Nathan or Adi can probably break it, but who cares?

    // Round 1
    tmpA = 0x0;
    tmpA ^= AES_PRECOMP_TE0[((in >> 24) ^ key[0]) & 0xFF];
    tmpA ^= AES_PRECOMP_TE1[((in >> 16) ^ key[1]) & 0xFF];
    tmpA ^= AES_PRECOMP_TE2[((in >> 8) ^ key[2]) & 0xFF];
    tmpA ^= AES_PRECOMP_TE3[((in >> 0) ^ key[3]) & 0xFF];

    // Round 2
    tmpB = 0x0;
    tmpB ^= AES_PRECOMP_TE0[((tmpA >> 24) ^ key[4]) & 0xFF];
    tmpB ^= AES_PRECOMP_TE1[((tmpA >> 16) ^ key[5]) & 0xFF];
    tmpB ^= AES_PRECOMP_TE2[((tmpA >> 8) ^ key[6]) & 0xFF];
    tmpB ^= AES_PRECOMP_TE3[((tmpA >> 0) ^ key[7]) & 0xFF];

    // Round 3
    tmpA = 0x0;
    tmpA ^= AES_PRECOMP_TE0[((tmpB >> 24) ^ key[8]) & 0xFF];
    tmpA ^= AES_PRECOMP_TE1[((tmpB >> 16) ^ key[9]) & 0xFF];
    tmpA ^= AES_PRECOMP_TE2[((tmpB >> 8) ^ key[10]) & 0xFF];
    tmpA ^= AES_PRECOMP_TE3[((tmpB >> 0) ^ key[11]) & 0xFF];

    // Round 4
    tmpB = 0x0;
    tmpB ^= AES_PRECOMP_TE0[((tmpA >> 24) ^ key[12]) & 0xFF];
    tmpB ^= AES_PRECOMP_TE1[((tmpA >> 16) ^ key[13]) & 0xFF];
    tmpB ^= AES_PRECOMP_TE2[((tmpA >> 8) ^ key[14]) & 0xFF];
    tmpB ^= AES_PRECOMP_TE3[((tmpA >> 0) ^ key[15]) & 0xFF];

    LOAD32H(tmpA, key);

    return tmpA ^ tmpB;
}
```

很明显，当 `key` 不变时，输入的 `in` 相同，则返回的数相同。

当时理解为产生随机数，导致移植时，我直接写了个生成独一无二的随机数的函数替代他。

这里就面临了个问题：

在 loopEntry 中，我生产了 LoadInst 指令：

```cpp
int defaultRandNum = rng.getRandom();
new StoreInst(
    ConstantInt::get(
        Type::getInt32Ty(f->getContext()),
        defaultRandNum
    ),
    switchVar, insert
);
load = new LoadInst(Type::getInt32Ty(f->getContext()), switchVar, "switchVar", loopEntry);
```

这里给 switchVar 赋了一个随机值。

然后在将原始基本块插入到 switch 指令中时，我又重新给 first 块一个新的随机数。

```cpp
for (
    std::vector<BasicBlock *>::iterator b = origBB.begin(); 
    b != origBB.end();
    ++b
) {
    BasicBlock *i = *b;
    ConstantInt *numCase = NULL;
    i->moveBefore(loopEnd);
    numCase = cast<ConstantInt>(
        ConstantInt::get(
            switchI->getCondition()->getType(),
            rng.getRandom()
        )
    );
    switchI->addCase(numCase, i);
}
```

这将导致程序根据一开始的随机值走入 switch，只会走到默认块中导致循环。

那原来的程序代码，则通过以下方式解决的：

一开始的 LoadInst 指令的随机数生成方式：

```cpp
new StoreInst(
    ConstantInt::get(
        Type::getInt32Ty(f->getContext()),
        llvm::cryptoutils->scramble32(0, scrambling_key)
    ),
    switchVar, insert
);
```

first 块的随机数的生成方式：（ first 块是第一个块，此时 `switchI->getNumCases()` 还为 `0` ）

```cpp
numCase = cast<ConstantInt>(
    ConstantInt::get(
        switchI->getCondition()->getType(),
        llvm::cryptoutils->scramble32(
            switchI->getNumCases(), 
            scrambling_key
        )
    )
);
```

这样子程序一开始就会走到 first 块。

所以这里要不就复制其生成 ID 的代码，要不写一个类似的。

#### 代码

##### Flattening.cpp

```cpp
#include "llvm/Pass.h"
#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Passes/PassBuilder.h"

#include "llvm/IR/Module.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Instructions.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/ADT/Statistic.h"
#include "llvm/Transforms/IPO.h"
#include "llvm/Transforms/Scalar.h"
#include "llvm/Transforms/Utils.h"
#include "llvm/Transforms/Utils/Local.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"
#include <vector>
#include <iostream>
#include <fstream>
#include <unordered_set>
#include <random>
#include <limits>
#include "./Utils.cpp"

using namespace llvm;

namespace
{
    cl::list<std::string> FunctionsToObfuscate("funcs", cl::desc("Specify function names to obfuscate"), cl::CommaSeparated);
    cl::opt<int> ObfTimes(
        "fla_loop",
        cl::desc("Choose how many time the flatten pass loops on a function"),
        cl::value_desc("number of times"),
        cl::init(1),
        cl::Optional);

    class Flattening : public PassInfoMixin<Flattening>
    {
    public:
        static bool isRequired() { return true; }
        static StringRef getPassName() { return "Flattening Pass"; }

        Flattening()
        {
        }

        PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM)
        {
            if (std::find(FunctionsToObfuscate.begin(), FunctionsToObfuscate.end(), F.getName()) == FunctionsToObfuscate.end())
            {
                return PreservedAnalyses::all();
            }
            if (ObfTimes <= 0)
            {
                errs() << "Flattening application number -fla_loop=x must be x > 0\n";
                return PreservedAnalyses::all();
            }
            errs() << "Obfuscating function: " << F.getName() << "\n";
            errs() << "Obfuscating Number: " << ObfTimes << "\n";
            for (int i = 0; i < ObfTimes; i++)
            {
                if (!flatten(&F))
                {
                    errs() << "Flattening failed\n";
                    return PreservedAnalyses::all();
                }
            }
            return PreservedAnalyses::all();
        }

        bool valueEscapes(Instruction *Inst)
        {
            BasicBlock *BB = Inst->getParent();
            for (Value::use_iterator UI = Inst->use_begin(), E = Inst->use_end(); UI != E; ++UI)
            {
                Instruction *I = cast<Instruction>(*UI);
                if (I->getParent() != BB || isa<PHINode>(I))
                {
                    return true;
                }
            }
            return false;
        }

        void fixStack(Function *f)
        {
            std::vector<PHINode *> tmpPhi;
            std::vector<Instruction *> tmpReg;
            BasicBlock *bbEntry = &*f->begin();

            do
            {
                tmpPhi.clear();
                tmpReg.clear();
                for (Function::iterator i = f->begin(); i != f->end(); ++i)
                {
                    for (BasicBlock::iterator j = i->begin(); j != i->end(); ++j)
                    {
                        if (isa<PHINode>(j))
                        {
                            PHINode *phi = cast<PHINode>(j);
                            tmpPhi.push_back(phi);
                            continue;
                        }
                        if (
                            !(isa<AllocaInst>(j) && j->getParent() == bbEntry) &&
                            (valueEscapes(&*j) || j->isUsedOutsideOfBlock(&*i)))
                        {
                            tmpReg.push_back(&*j);
                            continue;
                        }
                    }
                }
                for (unsigned int i = 0; i != tmpReg.size(); ++i)
                {
                    DemoteRegToStack(*tmpReg.at(i), f->begin()->getTerminator());
                }
                for (unsigned int i = 0; i != tmpPhi.size(); ++i)
                {
                    DemotePHIToStack(tmpPhi.at(i), std::optional<BasicBlock::iterator>(f->begin()->getTerminator()));
                }

            } while (tmpReg.size() != 0 || tmpPhi.size() != 0);
        }

        bool flatten(Function *f)
        {
            std::vector<BasicBlock *> origBB;
            BasicBlock *loopEntry;
            BasicBlock *loopEnd;
            LoadInst *load;
            SwitchInst *switchI;
            AllocaInst *switchVar;
            char scarmbling_key[16];
            cryptoutils::get_bytes(scarmbling_key, 16);
            for (Function::iterator i = f->begin(); i != f->end(); ++i)
            {
                BasicBlock *tmp = &*i;
                origBB.push_back(tmp);
                BasicBlock *bb = &*i;
                if (isa<InvokeInst>(bb->getTerminator()))
                {
                    return false;
                }
            }
            if (origBB.size() <= 1)
            {
                return false;
            }
            origBB.erase(origBB.begin());
            Function::iterator tmp = f->begin();
            BasicBlock *insert = &*tmp;

            BranchInst *br = NULL;
            if (isa<BranchInst>(insert->getTerminator()))
            {
                br = cast<BranchInst>(insert->getTerminator());
            }
            if ((br != NULL && br->isConditional()) || insert->getTerminator()->getNumSuccessors() > 1)
            {
                BasicBlock::iterator i = insert->end();
                if (insert->size() > 1)
                {
                    --i;
                }
                BasicBlock *tmpBB = insert->splitBasicBlock(i, "first");
                origBB.insert(origBB.begin(), tmpBB);
            }

            insert->getTerminator()->eraseFromParent();
            errs() << "Collecting basic blocks\n";
            switchVar = new AllocaInst(Type::getInt32Ty(f->getContext()), 0, "switchVar", insert);
            int defaultRandNum = cryptoutils::scramble32(0, scarmbling_key);
            new StoreInst(
                ConstantInt::get(
                    Type::getInt32Ty(f->getContext()),
                    defaultRandNum
                ),
                switchVar, insert
            );
            loopEntry = BasicBlock::Create(f->getContext(), "loopEntry", f, insert);
            loopEnd = BasicBlock::Create(f->getContext(), "loopEnd", f, insert);
            load = new LoadInst(Type::getInt32Ty(f->getContext()), switchVar, "switchVar", loopEntry);
            insert->moveBefore(loopEntry);
            BranchInst::Create(loopEntry, insert);
            BranchInst::Create(loopEntry, loopEnd);
            BasicBlock *swDefault = BasicBlock::Create(f->getContext(), "switchDefault", f, loopEnd);
            BranchInst::Create(loopEnd, swDefault);
            switchI = SwitchInst::Create(&*f->begin(), swDefault, 0, loopEntry);
            switchI->setCondition(load);
            f->begin()->getTerminator()->eraseFromParent();
            BranchInst::Create(loopEntry, &*f->begin());

            for (
                std::vector<BasicBlock *>::iterator b = origBB.begin();
                b != origBB.end();
                ++b)
            {
                BasicBlock *i = *b;
                ConstantInt *numCase = NULL;
                i->moveBefore(loopEnd);
                numCase = cast<ConstantInt>(
                    ConstantInt::get(
                        switchI->getCondition()->getType(),
                        cryptoutils::scramble32(switchI->getNumCases(), scarmbling_key)
                    )
                );
                switchI->addCase(numCase, i);
            }

            for (
                std::vector<BasicBlock *>::iterator b = origBB.begin();
                b != origBB.end();
                ++b)
            {
                BasicBlock *i = *b;
                ConstantInt *numCase = NULL;
                if (i->getTerminator()->getNumSuccessors() == 0)
                {
                    continue;
                }

                if (i->getTerminator()->getNumSuccessors() == 1)
                {
                    BasicBlock *succ = i->getTerminator()->getSuccessor(0);
                    i->getTerminator()->eraseFromParent();
                    numCase = switchI->findCaseDest(succ);
                    if (numCase == NULL)
                    {
                        numCase = cast<ConstantInt>(
                            ConstantInt::get(
                                switchI->getCondition()->getType(),
                                cryptoutils::scramble32(switchI->getNumCases(), scarmbling_key)    
                            )
                        );
                    }
                    new StoreInst(numCase, load->getPointerOperand(), i);
                    BranchInst::Create(loopEnd, i);
                    continue;
                }

                if (i->getTerminator()->getNumSuccessors() == 2)
                {
                    ConstantInt *numCaseTrue = switchI->findCaseDest(i->getTerminator()->getSuccessor(0));
                    ConstantInt *numCaseFalse = switchI->findCaseDest(i->getTerminator()->getSuccessor(1));
                    if (numCaseTrue == NULL)
                    {
                        numCaseTrue = cast<ConstantInt>(
                            ConstantInt::get(
                                switchI->getCondition()->getType(),
                                cryptoutils::scramble32(switchI->getNumCases(), scarmbling_key)
                            )
                        );
                    }
                    if (numCaseFalse == NULL)
                    {
                        numCaseFalse = cast<ConstantInt>(
                            ConstantInt::get(
                                switchI->getCondition()->getType(),
                                cryptoutils::scramble32(switchI->getNumCases(), scarmbling_key)
                            )
                        );
                    }
                    BranchInst *br = cast<BranchInst>(i->getTerminator());
                    SelectInst *sel = SelectInst::Create(
                        br->getCondition(),
                        numCaseTrue,
                        numCaseFalse,
                        "", i->getTerminator()->getIterator()
                    );
                    i->getTerminator()->eraseFromParent();
                    new StoreInst(sel, load->getPointerOperand(), i);
                    BranchInst::Create(loopEnd, i);
                    continue;
                }
            }
            fixStack(f);
            return true;
        }
    };
}

llvm::PassPluginLibraryInfo getFlatteningPluginInfo()
{
    return {
        LLVM_PLUGIN_API_VERSION, "Flattening", LLVM_VERSION_STRING,
        [](PassBuilder &PB)
        {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                   ArrayRef<PassBuilder::PipelineElement>)
                {
                    if (Name == "Flattening")
                    {
                        FPM.addPass(Flattening());
                        return true;
                    }
                    return false;
                });
        }};
}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo()
{
    return getFlatteningPluginInfo();
}
```

##### DemoteRegToStack.cpp

直接复制于 LLVM20 的源码。

##### Utils.cpp

```cpp
#include <fstream>
#include <iostream>
#include <cassert>
#define LOAD32H(x, y)                                                          \
    {                                                                            \
        (x) = ((uint32_t)((y)[0] & 0xFF) << 24) |                                  \
            ((uint32_t)((y)[1] & 0xFF) << 16) |                                  \
            ((uint32_t)((y)[2] & 0xFF) << 8) | ((uint32_t)((y)[3] & 0xFF) << 0); \
    }

class cryptoutils
{
public:
    void static get_bytes(char *buf, int len)
    {
#if defined(__linux__)
        std::ifstream devrandom("/dev/urandom");
#else
        std::ifstream devrandom("/dev/random");
#endif
        if (devrandom) {
            devrandom.read(buf, len);
            if (devrandom.gcount() != len) {
                std::cerr << "Cannot read enough bytes in /dev/random\n";
                return;
            }
            devrandom.close();
        }
    }

    unsigned static scramble32(const unsigned in, const char key[16]) {
        assert(key != NULL && "CryptoUtils::scramble key=NULL");
        unsigned tmpA, tmpB;
        // Round 1
        tmpA = 0x0;
        tmpA ^= AES_PRECOMP_TE0[((in >> 24) ^ key[0]) & 0xFF];
        tmpA ^= AES_PRECOMP_TE1[((in >> 16) ^ key[1]) & 0xFF];
        tmpA ^= AES_PRECOMP_TE2[((in >> 8) ^ key[2]) & 0xFF];
        tmpA ^= AES_PRECOMP_TE3[((in >> 0) ^ key[3]) & 0xFF];

        // Round 2
        tmpB = 0x0;
        tmpB ^= AES_PRECOMP_TE0[((tmpA >> 24) ^ key[4]) & 0xFF];
        tmpB ^= AES_PRECOMP_TE1[((tmpA >> 16) ^ key[5]) & 0xFF];
        tmpB ^= AES_PRECOMP_TE2[((tmpA >> 8) ^ key[6]) & 0xFF];
        tmpB ^= AES_PRECOMP_TE3[((tmpA >> 0) ^ key[7]) & 0xFF];

        // Round 3
        tmpA = 0x0;
        tmpA ^= AES_PRECOMP_TE0[((tmpB >> 24) ^ key[8]) & 0xFF];
        tmpA ^= AES_PRECOMP_TE1[((tmpB >> 16) ^ key[9]) & 0xFF];
        tmpA ^= AES_PRECOMP_TE2[((tmpB >> 8) ^ key[10]) & 0xFF];
        tmpA ^= AES_PRECOMP_TE3[((tmpB >> 0) ^ key[11]) & 0xFF];

        // Round 4
        tmpB = 0x0;
        tmpB ^= AES_PRECOMP_TE0[((tmpA >> 24) ^ key[12]) & 0xFF];
        tmpB ^= AES_PRECOMP_TE1[((tmpA >> 16) ^ key[13]) & 0xFF];
        tmpB ^= AES_PRECOMP_TE2[((tmpA >> 8) ^ key[14]) & 0xFF];
        tmpB ^= AES_PRECOMP_TE3[((tmpA >> 0) ^ key[15]) & 0xFF];

        LOAD32H(tmpA, key);

        return tmpA ^ tmpB;
    }
};
```

