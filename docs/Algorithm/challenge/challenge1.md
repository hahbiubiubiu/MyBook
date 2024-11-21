# 最长公共子序列

[最长公共子序列](https://www.acwing.com/problem/content/3513/)

若使用DP来做，`f[N][N]`对于`N≤1e6`来说，空间复杂度太大。

题目保证第一个序列中的所有元素均不重复，因此第二个序列的每个元素在第一个序列中的下标一定。

若有一个序列存储第二个序列每个元素在第一个序列的下标，则该序列的上升子序列所位置对应的第二个序列的子序列和该序列的上升子序列所下表对应的第一个序列的子序列为公共子序列。

因此问题转化为求该序列的最长上升子序列。

```c++
#include<iostream>
#include<algorithm>
using namespace std;

typedef long long LL;
const int N = 1e6+7;
int n;
int a[N], b[N], idx[N];
int temp[N], cnt = 0;

int main() {
    scanf("%d", &n);
    for (int j = 1; j <= n; j++){
        scanf("%d", &a[j]);
        idx[a[j]] = j;    
    }
    for (int j = 1; j <= n; j++){
        scanf("%d", &b[j]);
        b[j] = idx[b[j]];
    }
    for (int i = 1; i <= n; i++)
    {
        if (b[i] == 0)
            continue;
        
        if (cnt == 0 || temp[cnt-1] < b[i]) {
            temp[cnt++] = b[i];
        } else {
            int pos = lower_bound(temp, temp + cnt, b[i]) - temp;
            temp[pos] = b[i];
            // int l = 0, r = cnt - 1;
            // while (l < r) {
            //     int mid = l + r >> 1;
            //     if (temp[mid] < b[i]) l = mid + 1;
            //     else r = mid;
            // }
            // temp[l] = b[i];
        }
    }
    printf("%d\n", cnt);
    return 0;
}
```

