# 线性基

[线性基)](https://www.luogu.com.cn/problem/P3812)

给定 $n$ 个整数（数字可能重复），求在这些数中选取任意个，使得他们的异或和最大。

1. 对于一组数`A1...An`，他们的线性基为`P1...Pm` ，其中`Pi `是出现`1`的最高位在第`i`位的数
   1. `P`为线性基
   2. 线性空间$V$的一个极大线性无关组为$V$的一组线性基，简称基
2. 对原集合的每个数`p`转为二进制，从高位向低位扫，对于第`i`位是`1`的，如果`ai`不存在，那么令`ai = p`并结束扫描，如果存在，令`p = p ^ ai`
   1. 生成的`a`为原集合的线性基
3. 查询原集合内任意几个元素异或的最大值，只需将线性基从高位向低位扫，若异或上当前扫到的`ai`答案变大，就把答案异或上`ai`
   1. 从高往低位扫，若当前扫到第`i`位，意味着可以保证答案的第`i`位为`1`，且后面没有机会改变第`i`位
4. 考虑以下情况
   1. 对于数`x`，如果第`i`位是`1`且`ai`不存在，则`ai = x`
   2. 对于数`y`，如果第`i`位是`1`且`ai`存在，则`y = y ^ x`， 然后当`y`第`j`位是`1`且`aj`不存在，则`aj = y ^ x`
   3. 对于数`z`，如果第`i`位是`1`且`ai`存在，则`z = z ^ x`， 然后当`z`第`j`位是`1`且`aj`存在，则`z = z ^ x ^ (x ^ y) = z ^ y`，然后当`z`第`k`位是`1`且`ak`不存在，则`ak = z ^ y`
   4. 在将线性基从高位向低位扫时
      1. 如果已经取了`ai`，并且扫到第`j`位时，若`ans' ^ x = ans < ans ^ aj`，则`ans = ans ^ aj = ans ^ ai ^ y = ans' ^ y  (ans'为ans所有异或的数除了ai的异或和)`，这意味着`y`比`x`更能让异或和增大
   5. 以上，其实就是让第`i`位为`1`的几个数中选，尽量使第`i`位为`1`
      1. 组成最大异或和的数
         1. 有`x`，则异或`ai`
         2. 有`y`，则异或`ai ^ aj`
         3. 有`z`，则异或`ai ^ aj ^ ak`
         4. 有`x, y, z`，则异或`ai ^ ak`

```c++
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long ull;
const int N = 50 + 7;

int n;
ull a[65], ans = 0;

void insert(ull x)
{
    for (int i = 63; i >= 0; i--)
        if (x >> i * 1ull)
            if (a[i])
                x ^= a[i];
            else
            {
                a[i] = x;
                break;
            }
}

int main()
{
    scanf("%d", &n);
    ull x;
    for (int i = 0; i < n; i++)
    {
        scanf("%llu", &x);
        insert(x);
    }
    for (int i = 63; i >= 0; i--)
        ans = max(ans, a[i] ^ ans);
    printf("%llu\n", ans);
    return 0;
}
```

# 数独

[数独](https://www.acwing.com/problem/content/168/)

```c++
#include <bits/stdc++.h>
using namespace std;

#define lowbit(x) (x & -x)
const int N = 9;
char a[N * N];
int ones[1 << N], bitMap[1 << N];
int row[N], col[N], cell[N];

int getNum(int x, int y)
{
    return row[x] & col[y] & cell[x / 3 * 3 + y / 3];
}

int findNext()
{
    int nx = -1, ny = -1, mcnt = 10;
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            if (a[i * N + j] == '.')
            {
                int cnt = ones[getNum(i, j)];
                if (cnt < mcnt)
                {
                    mcnt = cnt;
                    nx = i, ny = j;
                }
            }
    return nx * 9 + ny;
}

bool dfs(int cnt)
{
    if (cnt == 0)
        return true;
    int temp = findNext();
    int x = temp / 9, y = temp % 9;
    for (int i = getNum(x, y); i; i -= lowbit(i))
    {
        int num = bitMap[lowbit(i)];
        a[temp] = num + '1';
        row[x] -= 1 << num;
        col[y] -= 1 << num;
        cell[x / 3 * 3 + y / 3] -= 1 << num;
        if (dfs(cnt - 1))
            return true;
        a[temp] = '.';
        row[x] += 1 << num;
        col[y] += 1 << num;
        cell[x / 3 * 3 + y / 3] += 1 << num;
    }
    return false;
}

void init()
{
    // 将每一行、每一列、每个九宫格的数字集合初始化为0b111111111
    for (int i = 0; i < 9; i++)
        row[i] = col[i] = cell[i] = (1 << N) - 1;
    memset(a, 0, sizeof a);
}

int main()
{
    // 存储每个数字的二进制表示中最低位1的位置
    for (int i = 0; i < N; i++)
        bitMap[1 << i] = i;

    // 存储每个数字的二进制表示中1的个数
    for (int i = 0; i < (1 << N); i++)
        for (int j = i; j; j -= lowbit(j))
            ones[i]++;

    while (true)
    {
        init();
        scanf("%s", a);
        if (strcmp(a, "end") == 0)
            break;
        int cnt = 0;
        for (int i = 0; i < 9; i++)
            for (int j = 0; j < 9; j++)
                if (a[i * 9 + j] == '.')
                    cnt++;
                else
                {
                    int num = a[i * 9 + j] - '1';
                    row[i] -= 1 << num;
                    col[j] -= 1 << num;
                    cell[i / 3 * 3 + j / 3] -= 1 << num;
                }
        if (dfs(cnt))
            printf("%s\n", a);
    }
    return 0;
}
```

# 木棒

[木棒](https://www.acwing.com/problem/content/169/)

```c++
#include <bits/stdc++.h>
using namespace std;

const int N = 64 + 5;
int n, sum, len;
int a[N];
bool st[N];

bool dfs(int num, int curLen, int idx)
{
    // num: 当前已经拼出了多少根木棍
    // curLen: 当前这根木棍已经拼了多长
    // idx: 当前枚举到了第几根木棍

    // 如果木棍拼完了，返回true
    if (num * len == sum)
        return true;
    // 如果当前这根木棍拼完了，递归拼下一根
    if (curLen == len)
        return dfs(num + 1, 0, 0);
    // 枚举出可以拼到当前的木棍中的木棍
    for (int i = idx; i < n; i++)
    {
        if (st[i])
            continue;
        // 如果当前木棍拼不进去，直接跳过
        if (curLen + a[i] > len)
            continue;
        st[i] = true;
        // 如果当前木棍拼进去后，递归拼下一段
        if (dfs(num, curLen + a[i], idx + 1))
            return true;
        st[i] = false;
        // 拼第一段木棍时，如果当前木棍拼不进去，直接返回false
        // 拼最后一段木棍时，如果当前木棍拼进去恰好拼完，但前面递归失败了，直接返回false
        if (curLen == 0 || curLen + a[i] == len)
            return false;
        // 跳过相同长度的木棍
        while (i + 1 < n && a[i] == a[i + 1])
            i++;
    }
    return false;
}

int main()
{
    while (true)
    {
        sum = 0;
        scanf("%d", &n);
        if (n == 0)
            break;
        for (int i = 0; i < n; i++)
        {
            scanf("%d", &a[i]);
            sum += a[i];
        }
        // 从大到小排序，优先拼大的木棍
        sort(a, a + n, greater<int>());
        len = a[0];
        while (true)
        {
            memset(st, 0, sizeof st);
            // len应该是sum的约数
            if (sum % len == 0 && dfs(0, 0, 0))
            {
                printf("%d\n", len);
                break;
            }
            len++;
        }
    }
    return 0;
}
```

# 数字游戏

小圆是一只小仓鼠。现在有一个$n×m$棋盘$A_{n×m}$，每个格子上有一个正整数$a_{ij}$ 。小圆初始站在棋盘的$(1,1)$位置（即最左上角），并面朝右边。小圆每次可以去往相邻的一个没有被经过的格子，如果小圆要去住的格子恰好在小圆面朝的方向，则不需要转向；否则，需要转向一次。而小圆最多转向上$k$次。小圆会将所有经过的格子上的数字按顺序写成一行得到一个“愉悦值”，例如他依次经过$(1,23,9,18)$，则得到的“愉悦值”为$123918$。请问小圆能走出多少种不同的路径，使得得到的“愉悦值”能被$7$整除（不需要走到底，符合条件可以随时停下）。

```c++
#include <bits/stdc++.h>
using namespace std;

const int N = 10 + 5;
int n, m, k, ans = 0;
int a[N][N];
int dx[4] = {0, 0, 1, -1}, dy[4] = {1, -1, 0, 0};
bool st[N][N];

int get_num(int a, int b)
{
    int t = b;
    while (b)
    {
        a *= 10;
        b /= 10;
    }
    return a + t;
}
// num: 所走路径组成的数
// direction: 小圆面对的方向（与dx、dy下标一致）
// k_: 目前还能转向的次数
void dfs(int x, int y, int num, int direction, int k_)
{
    if (k_ < 0)
        return;
    if (num % 7 == 0)
        ans++;
    num = num % 7;
    for (int i = 0; i < 4; i++)
    {
        int nx = x + dx[i], ny = y + dy[i];
        // 出界的情况
        if (nx < 1 || nx > n || ny < 1 || ny > m)
            continue;
        // 访问过的格子
        if (st[nx][ny])
            continue;
        // 要走的方向与面对的方向相同
        if (direction == i)
        {
            st[nx][ny] = true;
            dfs(nx, ny, get_num(num, a[nx][ny]), i, k_);
            st[nx][ny] = false;
        }
        // 要走的方向与面对的方向不同
        else
        {
            st[nx][ny] = true;
            dfs(nx, ny, get_num(num, a[nx][ny]), i, k_ - 1);
            st[nx][ny] = false;
        }
    }
}

int main()
{
    scanf("%d%d%d", &n, &m, &k);
    for (int i = 1; i <= n; i++)
        for (int j = 1; j <= m; j++)
            scanf("%d", &a[i][j]);
    st[1][1] = true;
    dfs(1, 1, a[1][1], 0, k);
    printf("%d\n", ans);
}
```

# 运输游戏

 小圆是一只小仓鼠。给定一张`n`个点`m`条边的无向图（点编号从`1`开始）。小圆初始时在`1`号点，他需要将食物一次性运送至`n`号点。

每条边有两个值`w`和`v`分别表示边的承重和过路费，即该边最多可通过重量为`w`的食物，且小圆经过该边要交上`v`的过路费。一旦小圆携带的食物重量超过`w`或小圆剩下的预算不足`v`，则不能通过该边。

已知小圆总预算是`c`，请问小圆最多能多重的食物从`1`号点运送到`n`号点。

1. 二分
   1. `l = 0, r = INF`
   2. 设置能带重量为`x`，进行BFS搜索，直到搜到`n`号点
      1. 忽略`w[i] < x`的边，因为包含该边的路径无法带重量为`x`的食物
      2. 控制花费小于`c`
   3. 如果能走到，则`w`的区间可以缩小为`[x, r]`
   4. 如果不能走到，则`w`的区间可以缩小为`[l, x-1]`

```c++
#include <iostream>
#include <algorithm>
#include <cstring>
#include <queue>

using namespace std;
const int N = 1e5 + 7, M = 2e5 + 7;
typedef pair<int, int> PII;
int n, m, c;
int w[M], v[M], ne[M], h[N], e[M], idx = 0;
bool st[N];

void add(int a, int b, int c, int d)
{
    w[idx] = c;
    v[idx] = d;
    e[idx] = b;
    ne[idx] = h[a];
    h[a] = idx++;
}

bool check(int x)
{
    memset(st, 0, sizeof st);
    queue<PII> q;
    q.push({1, 0});
    st[1] = true;
    while (q.size())
    {
        auto t = q.front();
        q.pop();
        int node = t.first, cost = t.second;
        if (node == n) return true;
        st[node] = false;
        for (int i = h[node]; ~i; i = ne[i])
        {
            int j = e[i];
            if (st[j]) continue;
            if (w[i] < x) continue;
            if (v[i] + cost > c) continue;
            st[j] = true;
            q.push({j, v[i] + cost});
        }
    }
    return false;
}

int main() 
{
    scanf("%d%d%d", &n, &m, &c);
    memset(h, -1, sizeof h);
    for (int i = 1; i <= m; i++)
    {
        int a, b, c, d;
        scanf("%d%d%d%d", &a, &b, &c, &d);
        add(a, b, c, d);
        add(b, a, c, d);
    }
    int l = 0, r = 1e9 + 1;
    while (l < r)
    {
        int mid = l + r >> 1;
        if (check(mid)) l = mid;
        else r = mid - 1;
    }
    printf("%d\n", l);
}
```

# 石子游戏

现有`n`堆石子排成一排，每堆石子有$a_i$颗。小圆需要从左到右选出$k$个不相交的区间，区间的长度分别为$1,2,⋯,k$，且满足这$k$个区间的石子总数单调递减。请问$k$最大能取多少。

1. `f[i][j]`：前`i`堆石子分为`j`个区间时，最后一个区间的总和的最大值
2. `f[i][j]`起始应该为``f[i - 1][j])`
3. 如果前`i - j`堆石子分为`j - 1`个区间时，最后一个区间的总和的最大值小于区间`[i-j, i]`的石子数，则可更新`f[i][j]`为`max(f[i][j], s[i] - s[i - j])`
4. `j`的范围为$\frac{j(j+1)}{2} < n$

```c++
#include <iostream>
#include <cstring>
#include <algorithm>
#include <cmath>

using namespace std;

const int N = 1e5 + 7;
const int M = 5e2 + 7;
int n, s[N], f[N][M];

int main()
{
    scanf("%d", &n);
    int m = sqrt(2 * n);
    for (int i = 1; i <= n; i++)
    {
        scanf("%d", &s[i]);
        s[i] += s[i - 1];
    }
    f[1][0] = 0;
    f[1][1] = s[1];
    for (int i = 2; i <= n; i++)
        for (int j = 1; j <= m; j++)
        {
            f[i][j] = f[i - 1][j];
            if (f[i - j][j - 1] > (s[i] - s[i - j]))
            {
                f[i][j] = max(f[i][j], s[i] - s[i - j]);
            }
        }
    int k = 1;
    while (f[n][k] != 0)
        k++;
    printf("%d\n", k - 1);
}
```

