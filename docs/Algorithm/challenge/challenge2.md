# HXY玩卡片

> HXY得到了一些卡片，这些卡片上标有数字 $0$ 或 $5$ 。现在她可以选择其中一些卡片排成一列，使得排出的一列数字组成的数最大，且满足被 $90$ 整除这个条件。同时，这个数必须为合法的某个非负整数，即不能含有前导 $0$ ，即 $0$ 不能作为这串数的首位。但是特殊地，整数 $0$ 满足条件。如果不能排出这样的数，输出“$-1$”。

分析题意可得：

1. 必须为10的倍数
2. 每位数字之和为9的倍数

```c++
#include <iostream>
using namespace std;

const int N = 1000 + 7;
int num0 = 0, num5 = 0;

int main() {
    int n;
    scanf("%d", &n);
    for (int i = 0; i < n; i++) {
        int x;
        scanf("%d", &x);
        if (x == 0) num0++;
        else num5++;
    }
    if (num0 == 0) {
        puts("-1");
        return 0;
    }
    if (num5 < 9) {
        puts("0");
        return 0;
    }
    num5 -= num5 % 9;
    for (int i = 0; i < num5; i++) {
        printf("5");
    }
    for (int i = 0; i < num0; i++) {
        printf("0");
    }
    return 0;
}
```

# 避雷针

> $n$ 个避雷针从左至右排成一排，我们将它们从左至右依次标号为 $1 \sim  n$。
>
> 现在有 $m$ 道雷依次劈下。你得知了一串序列 $a _ 1, \cdots, a _ m$。对于第 $i$ 道雷，其劈中了 $a _ i - 2$（如果存在）、$a _ i - 1$（如果存在）、$a _ i$、$a _ i + 1$（如果存在）、$a _ i + 2$（如果存在）号避雷针。
>
> 在 $m$ 道雷劈完后，你想要知道，被劈过**至少一次**的避雷针有几个。

```c++
#include <iostream>
#include <algorithm>
using namespace std;

const int N = 1e6 + 7;
int f[N] = {0};

int main() {
    int n, m;
    scanf("%d%d", &n, &m);
    for (int i = 0; i < m; i++) {
        int x, l, r;
        scanf("%d", &x);
        l = min(max(x - 2, 1), max(x - 1, 1));
        r = max(min(x + 1, n), min(x + 2, n));
        f[l] += 1;
        f[r + 1] -= 1;
    }
    int count = f[1] > 0;
    for (int i = 2; i <= n; i++) {
        f[i] += f[i - 1];
        if (f[i] > 0)
            count++;
    }
    printf("%d\n", count);
    return 0;
}
```

# 通天之分组背包

> 自 $01$ 背包问世之后，小 A 对此深感兴趣。一天，小 A 去远游，却发现他的背包不同于 $01$ 背包，他的物品大致可分为 $k$ 组，每组中的物品相互冲突，现在，他想知道最大的利用价值是多少。

1. `f[i][j]`：拿了前`i`组的物品重量为`j`的最大利用价值
2. $f[i][j] = max(f[i-1][j], \{f[i-1][j-w_{i,t}], w_{i,t}为第i组的第t个物品的重量\})$

```c++
#include <iostream>
#include <algorithm>
#include <cstring>
using namespace std;

const int N = 1e3 + 7;
int w[N], v[N], ne[N], h[107], idx, groupNum;
int f[107][N];
void add(int a, int b, int c)
{
    w[idx] = a;
    v[idx] = b;
    if (h[c] == -1)
        groupNum++;
    ne[idx] = h[c];
    h[c] = idx++;
}

int main()
{
    memset(h, -1, sizeof h);
    int n, m;
    scanf("%d%d", &m, &n);
    for (int i = 0; i < n; i++)
    {
        int a, b, c;
        scanf("%d%d%d", &a, &b, &c);
        add(a, b, c);
    }
    for (int i = 1; i <= groupNum; i++)
        for (int j = 1; j <= m; j++)
        {
            f[i][j] = f[i - 1][j];
            for (int k = h[i]; k != -1; k = ne[k])
                if (j >= w[k])
                    f[i][j] = max(f[i][j], f[i - 1][j - w[k]] + v[k]);
        }
    printf("%d", f[groupNum][m]);
    return 0;
}
```

# 泥泞路

> 暴雨过后，FJ 的农场到镇上的公路上有一些泥泞路，他有若干块长度为 $L$ 的木板可以铺在这些泥泞路上，问他至少需要多少块木板，才能把所有的泥泞路覆盖住。

1. 按照起点对泥泞路排序
2. 贪心，每次将最前面的泥泞路铺满，只向后延申

```c++
#include <iostream>
#include <algorithm>
#include <cstring>
#include <vector>
using namespace std;

const int N = 1e4 + 7;
vector<pair<int, int>> path;
bool compare(const pair<int, int>& a, const pair<int, int>& b) {
    return a.first < b.first;
}

int main()
{
    int n, len;
    scanf("%d%d", &n, &len);
    for (int i = 0; i < n; i++)
    {
        int s, e;
        scanf("%d%d", &s, &e);
        if (s == e) continue;
        path.push_back(make_pair(s, e));
    }
    sort(path.begin(), path.end(), compare);
    int count = 0, num, extra = 0, s = 0, e = 0;
    for (int i = 0; i < n; i++)
    {
        if (e + extra >= path[i].second)
            continue;
        extra = max(e + extra - path[i].first, 0);
        s = path[i].first;
        e = path[i].second;
        num = (e - (s + extra)) / len;
        num += ((e - (s + extra)) % len == 0) ? 0 : 1;
        extra = num * len - (e - (s + extra));
        count += num;
    }
    printf("%d\n", count);
    return 0;
}
```

# 迷宫寻路

> 机器猫被困在一个矩形迷宫里。
>
> 迷宫可以视为一个 $n\times m$ 矩阵，每个位置要么是空地，要么是墙。机器猫只能从一个空地走到其上、下、左、右的空地。
>
> 机器猫初始时位于 $(1, 1)$ 的位置，问能否走到 $(n, m)$ 位置。
>
> ### 样例输入
>
> ```
> 3 5
> .##.#
> .#...
> ...#.
> ```
>
> ### 样例输出
>
> ```
> Yes
> ```
>

1. 主要是输入，要注意回车符（damn）

```c++
#include <iostream>
#include <algorithm>
#include <queue>
using namespace std;

const int N = 1e2 + 7;
char map[N][N];
int n, m;

bool bfs()
{
    int dx[] = {0, 0, 1, -1}, dy[] = {1, -1, 0, 0};
    queue<pair<int, int>> q;
    q.push({1, 1});
    while (!q.empty())
    {
        auto t = q.front();
        q.pop();
        int x = t.first, y = t.second;
        if (x == n && y == m)
            return true;
        if (map[x][y] == '#')
            continue;
        map[x][y] = '#';
        for (int i = 0; i < 4; i++)
        {
            int a = x + dx[i], b = y + dy[i];
            if (a >= 1 && a <= n && b >= 1 && b <= m)
                q.push({a, b});
        }
    }
    return false;
}

int main()
{
    scanf("%d%d", &n, &m);
    for (int i = 1; i <= n; i++)
        scanf("%s", map[i]+1);
    if (bfs())
        puts("Yes");
    else
        puts("No");
    return 0;
}
```

# 最长的回文 Calf Flac

> 据说如果你给无限只母牛和无限台巨型便携式电脑（有非常大的键盘 ), 那么母牛们会制造出世上最棒的回文。你的工作就是去寻找这些牛制造的奇观（最棒的回文）。
>
> 在寻找回文时不用理睬那些标点符号、空格（但应该保留下来以便做为答案输出）, 只用考虑字母 ${\tt A}\sim {\tt Z}$ 和 ${\tt a}\sim {\tt z}$。要你寻找的最长的回文的文章是一个不超过 $20{,}000$ 个字符的字符串。我们将保证最长的回文不会超过 $2{,}000$ 个字符（在除去标点符号、空格之前）。
>
> ### 样例输入
>
> ```
> Confucius say: Madam, I'm Adam.
> ```
>
> ### 样例输出
>
> ```
> 11
> Madam, I'm Adam
> ```
>



## 自己的思路

一开始的思路**过不了示例：`lvlvlvlv`**，根据这个样例，特别判断了一下：（应该覆盖了所有的样例）

```c++
// 对于t~i-1的子串不是回文
// 判断后五个字母是不是abcba的形式
t1 = t - 1;
while(t1 && !isalpha(s[t1]))
    t1--;
int t2 = t1 - 1;
while(t2 && !isalpha(s[t2]))
    t2--;
int t3 = t2 - 1;
while(t3 && !isalpha(s[t3]))
    t3--;
if (s[t3] == s[i] && s[t2] == s[t])
{
    f[i][1][0] = t3;
    f[i][1][1] = i;
    f[i][1][2] = 5;
    continue;
}
```

1. `f[i][0]`：前面长度为`i`的字符串且不包括第`i`个字符的最长回文
   1. `f[i][0][0]`：该最长回文的起始位置
   2. `f[i][0][1]`：该最长回文的结尾位置
   3. `f[i][0][2]`：该最长回文的长度（不包括标点符号、空格）
2. `f[i][1]`：前面长度为`i`的字符串且包括第`i`个字符的最长回文长度
   1. `f[i][1][0]`：该最长回文的起始位置
   2. `f[i][1][1]`：该最长回文的结尾位置
   3. `f[i][1][2]`：该最长回文的长度（不包括标点符号、空格）

```c++
#include <iostream>
#include <algorithm>
#include <queue>
#include <cstring>
using namespace std;

const int N = 2e4 + 7;
char s[N], ori_s[N];
int f[N][2][3];

int main()
{
    char temp[200];
    while (cin.getline(temp, 200))
    {
        strcat(s + 1, temp);
        strcat(s + 1, "\n");
    }
    int len = strlen(s + 1);
    strncpy(ori_s + 1, s + 1, len);
    // 将s全部转换为小写
    transform(s + 1, s + len + 1, s + 1, ::tolower);
    // 找到最后一个字母，即为长度
    while(len && !isalpha(s[len]))
        len--;
    // 初始化
    f[2][0][0] = 1;
    f[2][0][1] = 1;
    f[2][0][2] = 1;
    f[2][1][0] = s[2] == s[1] ? 1 : 2;
    f[2][1][1] = 2;
    f[2][1][2] = s[2] == s[1] ? 2 : 1;

    for (int i = 3; i <= len; i++)
    {
        // 如果不是字母，跳过
        if (!isalpha(s[i]))
            continue;

        // 更新f[i][0]
        // 找到上一个字母
        int t = i - 1;
        while (t && !isalpha(s[t]))
            t--;
        // f[i][0]可以来源于f[t][0]或f[t][1]，哪个长取哪一个
        if (f[t][0][2] > f[t][1][2])
        {
            f[i][0][0] = f[t][0][0];
            f[i][0][1] = f[t][0][1];
            f[i][0][2] = f[t][0][2];
        }
        else if (f[t][0][2] < f[t][1][2])
        {
            f[i][0][0] = f[t][1][0];
            f[i][0][1] = f[t][1][1];
            f[i][0][2] = f[t][1][2];
        }
        else
        {
            // 如果一样长，则取最先出现的
            if (f[t][0][0] >= f[t][1][0])
            {
                f[i][0][0] = f[t][1][0];
                f[i][0][1] = f[t][1][1];
                f[i][0][2] = f[t][1][2];
            }
            else
            {
                f[i][0][0] = f[t][0][0];
                f[i][0][1] = f[t][0][1];
                f[i][0][2] = f[t][0][2];
            }
        }

        // 更新f[i][1]
        f[i][1][0] = i;
        f[i][1][1] = i;
        f[i][1][2] = 1;

        // 对于t~i-1的子串是回文的情况，比较t-1和i是否相同
        int t1 = f[t][1][0] - 1;
        while(t1 && !isalpha(s[t1]))
            t1--;
        if (s[i] == s[t1])
        {
            f[i][1][0] = t1;
            f[i][1][1] = i;
            f[i][1][2] = f[t][1][2] + 2;
            continue;
        }

        // 对于t~i-1的子串不是回文
        // 判断后五个字母是不是abcba的形式
        t1 = t - 1;
        while(t1 && !isalpha(s[t1]))
            t1--;
        int t2 = t1 - 1;
        while(t2 && !isalpha(s[t2]))
            t2--;
        int t3 = t2 - 1;
        while(t3 && !isalpha(s[t3]))
            t3--;
        if (s[t3] == s[i] && s[t2] == s[t])
        {
            f[i][1][0] = t3;
            f[i][1][1] = i;
            f[i][1][2] = 5
            continue;
        }
        // 判断后三个字母是不是aba的形式
        if (s[i] == s[t1])
        {
            f[i][1][0] = t1;
            f[i][1][1] = i;
            f[i][1][2] = 3;
            continue;
        }
        // 判断后两个字母是不是aa的形式
        if (s[i] == s[t])
        {
            f[i][1][0] = t;
            f[i][1][1] = i;
            f[i][1][2] = 2;
            continue;
        }

    }
    char ans[N];
    if (f[len][0][2] > f[len][1][2])
    {
        strncpy(ans, ori_s + f[len][0][0], f[len][0][1] - f[len][0][0] + 1);
        printf("%d\n", f[len][0][2]);
        printf("%s", ans);
    }
    else if (f[len][0][2] < f[len][1][2])
    {
        strncpy(ans, ori_s + f[len][1][0], f[len][1][1] - f[len][1][0] + 1);
        printf("%d\n", f[len][1][2]);
        printf("%s", ans);
    }
    else
    {
        if (f[len][0][0] >= f[len][1][0])
        {
            strncpy(ans, ori_s + f[len][1][0], f[len][1][1] - f[len][1][0] + 1);
            printf("%d\n", f[len][1][2]);
            printf("%s", ans);
        }
        else
        {
            strncpy(ans, ori_s + f[len][0][0], f[len][0][1] - f[len][0][0] + 1);
            printf("%d\n", f[len][0][2]);
            printf("%s", ans);
        }
    }
    return 0;
}
```

# 修复公路

> A 地区在地震过后，连接所有村庄的公路都造成了损坏而无法通车。政府派人修复这些公路。
>
> 给出 A 地区的村庄数 $N$，和公路数 $M$，公路是双向的。并告诉你每条公路的连着哪两个村庄，并告诉你什么时候能修完这条公路。问最早什么时候任意两个村庄能够通车，即最早什么时候任意两条村庄都存在至少一条修复完成的道路（可以由多条公路连成一条道路）。
>

1. 使用并查集，连通的村庄在一个集合，有同一个父节点
2. 所有修复可以同时开工，将根据道路修复时间从小到大排序
3. 每次找最小的，将两个村庄化为一个集合，即其中一个村庄的父节点认另一个村庄的父节点为父亲

```c++
#include <iostream>
#include <algorithm>
#include <vector>

using namespace std;
const int N = 1e3 + 10;
const int M = 1e5 + 10;

int n, m;
int p[N] = {0}, num[N];
vector<pair<int, pair<int, int>>> edge;

bool compare(const pair<int, pair<int, int>> &a, const pair<int, pair<int, int>> &b)
{
    return a.first < b.first;
}

int find(int x)
{
    while (p[x] != x)
        x = p[x];
    return x;
}

int main()
{
    scanf("%d%d", &n, &m);
    for (int i = 0; i < m; i++)
    {
        int a, b, c;
        scanf("%d%d%d", &a, &b, &c);
        edge.push_back({c, {a, b}});
    }
    sort(edge.begin(), edge.end(), compare);
    for (int i = 1; i <= n; i++)
        p[i] = i, num[i] = 1;

    for (int i = 0; i < m; i++)
    {
        int a = edge[i].second.first, b = edge[i].second.second, c = edge[i].first;
        int pa = find(a), pb = find(b);
        if (pa != pb)
        {
            p[pa] = pb;
            num[pb] += num[pa];
            if (num[pb] == n)
            {
                printf("%d\n", c);
                return 0;
            }
        }
    }
    printf("-1\n");
    return 0;
}
```

# 外星密码

> 有了防护伞，并不能完全避免 2012 的灾难。地球防卫小队决定去求助外星种族的帮助。经过很长时间的努力，小队终于收到了外星生命的回信。但是外星人发过来的却是一串密码。只有解开密码，才能知道外星人给的准确回复。解开密码的第一道工序就是解压缩密码，外星人对于连续的若干个相同的子串 $\texttt{X}$ 会压缩为 $\texttt{[DX]}$ 的形式（$D$ 是一个整数且 $1\leq D\leq99$），比如说字符串 $\texttt{CBCBCBCB}$ 就压缩为 $\texttt{[4CB]}$ 或者$\texttt{[2[2CB]]}$，类似于后面这种压缩之后再压缩的称为二重压缩。如果是 $\texttt{[2[2[2CB]]]}$ 则是三重的。现在我们给你外星人发送的密码，请你对其进行解压缩。

1. 使用堆栈来匹配中括号，并且记录起始位置和倍数
2. 匹配到一对中括号时，出栈，按照起始位置和倍数复制括号中的字符

```c++
#include <iostream>
#include <algorithm>
#include <stack>
#include <cstring>

using namespace std;
const int N = 2e4 + 10;
char s[N], ans[N];
int idx = 0;
stack<pair<int, int>> t;

int main()
{
    scanf("%s", s + 1);
    int n = strlen(s + 1);
    int i = 1;
    while (i <= n)
    {
        if (isalpha(s[i]))
        {
            ans[idx++] = s[i++];
            continue;
        }
        if (s[i] == '[')
        {
            int num = 0;
            while (isdigit(s[++i]))
                num = num * 10 + s[i] - '0';
            t.push({idx, num});
            continue;
        }
        if (s[i++] == ']')
        {
            auto temp = t.top();
            t.pop();
            int start = temp.first, len = idx - temp.first, times = temp.second;
            for (int j = 0; j < times - 1; j++)
                for (int k = 0; k < len; k++)
                    ans[idx++] = ans[start + k];
        }
    }
    ans[idx] = '\0';
    printf("%s", ans);
    return 0;
}
```

# 纪念邮票

> 邮局最近推出了一套纪念邮票，这套邮票共有 $N$ 张，邮票面值各不相同，按编号顺序为 $1$ 分，$2$ 分，……，$N$ 分。
>
> 小明是个集邮爱好者，他很喜欢这套邮票，可惜现在他身上只有 $M$ 分，并不够把全套都买下，但是他希望刚好花光所有的钱。作为一个集邮爱好者，小明也不想买的邮票编号断断续续，所以小明打算买面值 $a$ 分至 $b$ 分的 $b-a+1$ 张连续的邮票，且总价值刚好为 $M$ 分。
>
> 你的任务是求出所有符合要求的方案，以 $\left[a,b\right]$ 的形式输出。

```c++
#include <iostream>
#include <algorithm>
#include <cmath>

using namespace std;

int main()
{
    int n, m;
    scanf("%d%d", &n, &m);
    // (l + r) * len / 2 = m
    // (l + r) * len = 2 * m
    // l + r > len -> len < sqrt(2 * m)

    // 遍历len
    for (int i = sqrt(2 * m); i > 0; i--)
    {
        if (m * 2 % i)
            continue;
        int lr = m * 2 / i;
        int l, r;
        // lr = l + r = l + l + len - 1
        // l = (lr - len + 1) / 2 应该为整数，即lr - len + 1为偶数
        if ((lr - i + 1) % 2 != 0)
            continue;
        l = (lr - i + 1) / 2;
        r = (lr + i - 1) / 2;
        if (l > 0 && r <= n)
            printf("[%d,%d]\n", l, r);
    }
    return 0;
}
```

# 导弹拦截

> 某国为了防御敌国的导弹袭击，发展出一种导弹拦截系统。但是这种导弹拦截系统有一个缺陷：虽然它的第一发炮弹能够到达任意的高度，但是以后每一发炮弹都不能高于前一发的高度。某天，雷达捕捉到敌国的导弹来袭。由于该系统还在试用阶段，所以只有一套系统，因此有可能不能拦截所有的导弹。
>
>
> 输入导弹依次飞来的高度，计算这套系统最多能拦截多少导弹，如果要拦截所有导弹最少要配备多少套这种导弹拦截系统。
>

1. 第一问就是求最长不增长子序列的长度
2. 第二问
   1. 根据Dilworth定理：对于一个偏序集，最少链划分等于最长反链长度
   2. 最长上升子序列的长度就是能构成的不上升序列的个数，因此要使用导弹的次数就是最长上升子序列的长度。

```c++
#include <iostream>
#include <algorithm>
#include <cstring>
#include <string.h>
using namespace std;
const int N = 1e5 + 7;
int height[N], len = 0;
bool st[N];


int main()
{
    memset(st, 0, sizeof st);
    int x;
    while (scanf("%d", &x) != EOF)
        height[len++] = x;
    int q[N] = {0}, qlen = 0;
    for (int i = 0; i < len; i++)
    {
        int l = 0, r = qlen;
        while (l < r)
        {
            int mid = (l + r) >> 1;
            if (q[mid] >= height[i]) l = mid + 1;
            else r = mid;
        }
        q[l] = height[i];
        if (l == qlen) qlen++;
    }
    printf("%d\n", qlen);

    memset(q, 0, sizeof q);
    qlen = 0;
    for (int i = 0; i < len; i++)
    {
        int l = 0, r = qlen;
        while (l < r)
        {
            int mid = (l + r) >> 1;
            if (q[mid] < height[i]) l = mid + 1;
            else r = mid;
        }
        q[l] = height[i];
        if (l == qlen) qlen++;
    }
    printf("%d\n", qlen);
    
    return 0;
}
```

# 自我数

> 在 1949 年印度数学家 D. R. Daprekar 发现了一类称作 Self-Numbers 的数。对于每一个正整数 $n$，我们定义 $d(n)$ 为 $n$ 加上它每一位数字的和。例如， $d(75) = 75 + 7 + 5 = 87$。给定任意正整数 $n$ 作为一个起点，都能构造出一个无限递增的序列：$n, d(n), d(d(n)), d(d(d(n))), \ldots$ 例如，如果你从 $33$ 开始，下一个数是 $33 + 3 + 3 = 39$，再下一个为 $39 + 3 + 9 = 51$，再再下一个为 $51 + 5 + 1 = 57$，因此你所产生的序列就像这样：$33, 39, 51, 57, 69, 84, 96, 111, 114, 120, 123, 129, 141, \ldots$。数字 $n$ 被称作 $d(n)$ 的发生器。在上面的这个序列中，$33$ 是 $39$ 的发生器，$39$ 是 $51$ 的发生器，$51$ 是 $57$ 的发生器等等。有一些数有超过一个发生器，如 $101$ 的发生器可以是 $91$ 和 $100$。一个没有发生器的数被称作 Self-Number。如前 $13$ 个 Self-Number 为 $1, 3, 5, 7, 9, 20, 31, 42, 53, 64, 75, 86, 97$。我们将第 $i$ 个 Self-Number 表示为 $a_i$，所以 $a_1 = 1, a_2 = 3, a_3 = 5, \ldots$。

1. 限制好像是空间
2. 枚举每一个数`x`，为`d(x)`做标记，若`x`没被标记，则代表其为自我数，将该数存下来
3. 由于`d(x) - x < 100`，做标记时的下标可以模100，使标记数组不需要这么大
4. 使用`bitset<10000001>`

```c++
#include <iostream>
#include <algorithm>
using namespace std;
const int N = 1e6 + 7;
int calc(int x)
{
    int sum = x;
    while (x)
    {
        sum += x % 10;
        x /= 10;
    }
    return sum;
}

int main()
{
    int n, k;
    scanf("%d%d", &n, &k);
    bool st[101] = {0};
    int num[N], idx = 0;
    for (int i = 1; i <= n; i++)
    {
        st[calc(i) % 100] = true;
        if (!st[i % 100])
            num[++idx] = i;
        st[i % 100] = false;
    }
    printf("%d\n", idx);
    for (int i = 0; i < k; i++)
    {
        int t;
        scanf("%d", &t);
        printf("%d ", num[t]);
    }
    return 0;
}
```

# 瑞瑞的木棍

> 瑞瑞有一堆的玩具木棍，每根木棍的两端分别被染上了某种颜色，现在他突然有了一个想法，想要把这些木棍连在一起拼成一条线，并且使得木棍与木棍相接触的两端颜色都是相同的，给出每根木棍两端的颜色，请问是否存在满足要求的排列方式。
>
> 例如，如果只有 2 根木棍，第一根两端的颜色分别为 red, blue，第二根两端的颜色分别为 red, yellow，那么 blue---red | red----yellow 便是一种满足要求的排列方式。
>

1. 题目可以抽象为：
   1. 每个颜色是一个点，每根木棍是一个边
   2. 能否找到一条经过所有边且每条边只经过一次的路径
2. 能否找到一条经过所有边且每条边只经过一次的路径取决于所有点是否连通且奇数度的点为0或者2

使用map版本，TLE了

```c++
#include <iostream>
#include <algorithm>
#include <map>
#include <cstring>
using namespace std;

const int N = 250000 * 2 + 7;
int p[N];

int find(int x)
{
    while (p[x] != x)
        x = p[x];
    return x;
}

int main()
{
    int din[N] = {0}, colorNum = 0;
    memset(p, -1, sizeof p);
    map<string, int> color;
    string str1, str2;
    while (cin >> str1 >> str2)
    {
        if (color.find(str1) == color.end())
        {
            color[str1] = colorNum;
            p[colorNum] = colorNum;
            din[colorNum] = 1;
            colorNum++;
        }
        else
            din[color[str1]]++;
        if (color.find(str2) == color.end())
        {
            color[str2] = colorNum;
            p[colorNum] = colorNum;
            din[colorNum] = 1;
            colorNum++;
        }
        else
            din[color[str2]]++;
        p[find(color[str1])] = find(color[str2]);
    }
    int count = 0, parent = find(0);
    for (auto it = color.begin(); it != color.end(); it++)
    {
        if (find(it->second) != parent)
        {
            cout << "Impossible" << endl;
            return 0;
        }
        if (din[it->second] % 2 == 1)
            count++;
    }
    if (count == 0 || count == 2)
        cout << "Possible" << endl;
    else
        cout << "Impossible" << endl;
    return 0;
}
```

使用字符串哈希版本：

```c++
#include <iostream>
#include <algorithm>
#include <cstring>
using namespace std;

const int N = 250000 * 2 + 7;
const int mod = 1e6;
int p[mod], din[mod];

int find(int x)
{
    while (p[x] != x)
        x = p[x];
    return x;
}

int stringHash(string str)
{
    int hash = 0;
    for (int i = 0; i < str.size(); i++)
        hash = (hash * 131 + str[i]) % mod;
    return hash;
}

int main()
{
    memset(p, -1, sizeof p);
    string str1, str2;
    int dinNum = 0, groupNum = 0;
    while (cin >> str1 >> str2)
    {
        int t1 = stringHash(str1);
        if (din[t1] == 0)
        {
            p[t1] = t1;
            din[t1]++;
            groupNum++;
            dinNum++;
        }
        else
        {
            din[t1]++;
            if (din[t1] & 1)
                dinNum++;
            else
                dinNum--;
        }
        int t2 = stringHash(str2);
        if (din[t2] == 0)
        {
            p[t2] = t2;
            din[t2]++;
            groupNum++;
            dinNum++;
        }
        else
        {
            din[t2]++;
            if (din[t2] & 1)
                dinNum++;
            else
                dinNum--;
        }
        if (find(t1) != find(t2))
        {
            p[find(t1)] = find(t2);
            groupNum --;
        }
    }

    if (groupNum < 2 && (dinNum == 0 || dinNum == 2))
        printf("Possible");
    else
        printf("Impossible");
    return 0;
}
```

## 欧拉回路

[3225. 送货 - AcWing题库](https://www.acwing.com/problem/content/description/3228/)

```c++
#include <bits/stdc++.h>
using namespace std;

const int N = 1e4 + 7;
const int M = 2e5 + 7;
int h[N], ne[M], e[M], idx = 0;
int n, m, din[N], ans[M], cnt = 0;
bool st[M];

void add(int a, int b)
{
    e[idx] = b;
    ne[idx] = h[a];
    h[a] = idx;
    idx++;
}

void dfs(int u)
{
    vector<pair<int, int>> next;
    for (int i = h[u]; i != -1; i = ne[i])
        if (!st[i])
            next.push_back({e[i], i});
    sort(next.begin(), next.end());
    for (auto &it : next)
    {
        // 之所以要再次判断，是因为前面循环的dfs可能走过了他
        if (st[it.second])
            continue;
        st[it.second] = st[it.second ^ 1] = true;
        dfs(it.first);
    }
    ans[cnt++] = u;
    return;
}

int main()
{
    memset(h, -1, sizeof h);
    scanf("%d%d", &n, &m);
    int a, b;
    for (int i = 0; i < m; i++)
    {
        scanf("%d%d", &a, &b);
        add(a, b);
        add(b, a);
        din[a]++;
        din[b]++;
    }
    int count = 0;
    for (int i = 1; i <= n; i++)
        if (din[i] % 2)
            count++;
    if ((count != 0 && count != 2) || (count == 2 && din[1] % 2 == 0))
    {
        printf("-1");
        return 0;
    }
    dfs(1);
    if (cnt < m)
        printf("-1");
    else
        for (int i = cnt - 1; i >= 0; i--)
            printf("%d ", ans[i]);
    return 0;
}
```

# 最大子段和

> 给出一个长度为 $n$ 的序列 $a$，选出其中连续且非空的一段使得这段和最大。
>

1. `ti`为前`i`个`a`的最大子段和
2. `sum`为前`i`个`a`的前缀和
   1. 每次`sum < 0`，`sum`就清零
   2. 假设`1~x`的`a`计算的`sum < 0`，对于在第`x+1`轮来说，`sum + a_x+1 < a_x+1`，因此`a_x+1`绝对不会与`a_1~x`组成最大子段和
   3. `a_x+1`是否能和`a_y~x`组成最大子段和呢？
      1. 不能。
      2. 因为`1~x`的`a`计算的`sum < 0`，所以`a_x < 0`。若`a_x >= 0`，则遍历到`sum_x`时，会先清零，这样`sum_x = a_x > 0`

```c++
#include <bits/stdc++.h>
using namespace std;
const int N = 2e5 + 10;
int n, a[N];

int main()
{
    scanf("%d", &n);
    for (int i = 1; i <= n; i++)
        scanf("%d", &a[i]);
    int sum = a[1], res = a[1];
    for (int i = 2; i <= n; i++)
    {
        if (sum < 0) sum = 0;
        sum += a[i];
        res = max(res, sum);
    }
    printf("%d\n", res);
    return 0;
}
```

# 小朋友的数字

> 有 $n$ 个小朋友排成一列。每个小朋友手上都有一个数字，这个数字可正可负。规定每个小朋友的特征值等于排在他前面（包括他本人）的小朋友中连续若干个（最少有一个）小朋友手上的数字之和的最大值。
>
> 作为这些小朋友的老师，你需要给每个小朋友一个分数，分数是这样规定的：第一个小朋友的分数是他的特征值，其它小朋友的分数为排在他前面的所有小朋友中（不包括他本人），小朋友分数加上其特征值的最大值。
>
> 请计算所有小朋友分数的最大值，输出时保持最大值的符号，将其绝对值对 $p$ 取模后输出。

1. 数字`a[N]`
2. 特征值`t[N]`：最大子段和
3. 分数`g[i]`：`g[i] = max(g[i - 1], g[i - 1] + t[i - 1]) (i > 2)`
   1. 如果`t[i-1] < 0`，则`g[i] = g[i - 1]`
   2. `g[i]`是不降的
   3. `g[n] = g[2] + t[x1] + t[x2] ...  (t[x] > 0)`
4. `所有小朋友分数的最大值 = max(g[n], g[1])`
5. 本题要求最后结果模`p`
   1. 如果在运算过程中模`p`，无法判断最后`max(g[n], g[1])`的真实结果
   2. 如果在运算过程中不模`p`，最后结果可能超过`long long`类型的限制
   3. 在运算过程中，当检测到`g[i] > g[0]`，开始对`g[i]`模`p`，之后结果使用`g[n]`
6. 要对`n=2`的情况特殊判断一下

```c++
#include <bits/stdc++.h>
using namespace std;

const int N = 1e6 + 7;
int n, p;
int a[N];
long long t[N];

int main()
{
    long long sum, maxScore;
    scanf("%d%d", &n, &p);
    for (int i = 1; i <= n; i++)
        scanf("%d", &a[i]);
    t[1] = sum = a[1];
    for (int i = 2; i <= n; i++)
    {
        if (sum < 0)
            sum = 0;
        sum += a[i];
        t[i] = max(t[i - 1], sum);
    }
    // 如果a_2 < 0
    // g[2] = max(g[1], g[1] + t[1]) != g[1] + t[1]
    bool flag = false;
    maxScore = a[1] + t[1];
    for (int i = 3; i <= n; i++)
    {
        maxScore = max(maxScore, maxScore + t[i - 1]);
        if (maxScore > a[1])
            maxScore %= p, flag = true;
    }
    if (n == 2) maxScore = max(t[1], a[1] + t[1]) % p;
    else maxScore = flag ? maxScore : a[1] % p;
    printf("%d\n", maxScore);
    return 0;
}
```

# 国王游戏

> 恰逢 H 国国庆，国王邀请 $n$ 位大臣来玩一个有奖游戏。首先，他让每个大臣在左、右手上面分别写下一个整数，国王自己也在左、右手上各写一个整数。然后，让这 $n$ 位大臣排成一排，国王站在队伍的最前面。排好队后，所有的大臣都会获得国王奖赏的若干金币，每位大臣获得的金币数分别是：排在该大臣前面的所有人的左手上的数的乘积除以他自己右手上的数，然后向下取整得到的结果。
>
> 国王不希望某一个大臣获得特别多的奖赏，所以他想请你帮他重新安排一下队伍的顺序，使得获得奖赏最多的大臣，所获奖赏尽可能的少。注意，国王的位置始终在队伍的最前面。
>

## 理解一

假设大臣左手数为`A`，右手数为`B`

假设当前的排队方案不是按$A_x*B_x < A_{x+1}*B_{x+1}$从小到大排序的，则一定存在某两个相邻的人，满足$A_x*B_x >A_{x+1}*B_{x+1}$

将这两人位置互换，结果每一项除以  $(\prod\limits_{i=0}^{x-1}A_i)/(B_x*B_{x+1})$

|        | 第x位大臣的奖赏 | 第x+1位大臣的奖赏 |
| ------ | --------------- | ----------------- |
| 交换前 | $B_{x+1}$       | $A_x*B_x$         |
| 交换后 | $B_x$           | $A_{x+1}*B_{x+1}$ |

1. $A_x > 0 且为整数 \Rightarrow A_x*B_x > B_x$

2. $A_x*B_x >A_{x+1}*B_{x+1}$

此时，交换后两个数的最大值不大于交换前两个数的最大值，且交换这两个数不影响其他人的奖金

因此如果存在这种情况，则将其交换，得到的结果一定不会比原来差。

所以$A_x*B_x$从小到大排好序的序列就是最优解。

## 理解二

所有大臣的左手数字固定，因此所有大臣的左手数字的乘积一定。

对于最后一个大臣来说，其奖赏为 $(\prod\limits_{i=0}^{x-1}A_i)/B_x = ((\prod\limits_{i=0}^{x-1}A_i) * A_x)/(A_x * B_x)(\prod\limits_{i=0}^{x}A_i)/(A_x * B_x)$

因此$A_x*B_x$越大，该大臣的奖赏越小。

## code

代码难度主要是需要使用高精度乘法和除法，否则容易爆`long long`

高精度乘法：

假设 `123 * 456`

1. 枚举 `3 * 6`
2. 枚举 `3 * 5 + 2 * 6`
3. 枚举 `3 * 4 + 2 * 5 + 1 * 6`
4. 枚举 `2 * 4 + 1 * 5`
5. 枚举 `1 * 4`



```c++
vector<int> mul(vector<int> a, vector<int> b)
{
    vector<int> c;
    int carry = 0, temp;
    for (int i = 0; i < a.size() + b.size() - 1; i++)
    {
        temp = carry;
        for (int j = 0; j < a.size(); j++)
        {
            if (i - j >= 0 && i - j < b.size())
            {
                temp += a[j] * b[i - j];
            }
        }
        c.push_back(temp % 10);
        carry = temp / 10;
    }
    while (carry)
    {
        c.push_back(carry % 10);
        carry /= 10;
    }
    return c;
}
```



```c++
#include <bits/stdc++.h>
#include <vector>
using namespace std;
const int N = 1e3 + 10;
int n, l[N], r[N], R[N], L[N];
pair<int, int> g[N];

bool compare(const vector<int> &a, const vector<int> &b)
{
    if (a.size() != b.size())
    {
        return a.size() < b.size();
    }
    for (int i = a.size() - 1; i >= 0; i--)
    {
        if (a[i] != b[i])
        {
            return a[i] < b[i];
        }
    }
    return false;
}

vector<int> mul(vector<int> &A, int b)
{
    vector<int> C;
    int t = 0;
    for (int i = 0; i < A.size() || t; i ++ )
    {
        if (i < A.size()) t += A[i] * b;
        C.push_back(t % 10);
        t /= 10;
    }
    while (C.size() > 1 && C.back() == 0) C.pop_back();
    return C;
}

vector<int> div(vector<int> a, int b)
{
    vector<int> c;
    int carry = 0, temp;
    for (int i = a.size() - 1; i >= 0; i--)
    {
        temp = a[i] + carry * 10;
        c.push_back(temp / b);
        carry = temp % b;
    }
    reverse(c.begin(), c.end());
    while (c.size() > 1 && c.back() == 0)
        c.pop_back();
    return c;
}

vector<int> int2vector(int x)
{
    vector<int> a;
    while (x)
    {
        a.push_back(x % 10);
        x /= 10;
    }
    return a;
}

int main()
{
    scanf("%d", &n);
    for (int i = 0; i <= n; i++)
        scanf("%d%d", &l[i], &r[i]);

    for (int i = 1; i <= n; i++)
        g[i] = {l[i] * r[i], i};
    sort(g + 1, g + n + 1);
    for (int i = 1; i <= n; i++)
    {
        int idx = g[i].second;
        L[i] = l[idx];
        R[i] = r[idx];
    }
    vector<int> ans, mm;
    mm = int2vector(l[0]);
    ans = div(mm, R[1]);
    for (int i = 2; i <= n; i++)
    {
        mm = mul(mm, L[i - 1]);
        if (compare(ans, div(mm, R[i])))
            ans = div(mm, R[i]);
    }
    printVector(ans);
    return 0;
}
```

