# DNS服务器版本信息查询

1. **hostname.bind**:
   - 用于获取DNS服务器的主机名。在BIND中，可以通过发送一个针对`CH TXT "hostname.bind."`的请求来尝试获取该DNS服务器的主机名称。
2. **id.server**:
   - 用于获得DNS服务器的身份标识符。这通常是一个唯一的字符串，可以帮助识别具体的DNS服务器实例。通过向DNS服务器发送`CH TXT "id.server."`请求可以得到这个标识符。
3. **version.server**:
   - 用于获取DNS服务器软件的版本号。通过发送`CH TXT "version.server."`请求给DNS服务器，可以获得当前正在运行的DNS服务器软件版本信息。
4. **version.bind**:
   - 这个查询特别指BIND DNS软件的版本信息。与`version.server`类似，但更具体地指向BIND实现。通过发送`CH TXT "version.bind."`请求可以直接获取BIND的具体版本号。

# DNS查询-C实现

```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <unistd.h>

char dns_servers[16]; // 存放DNS服务器的IP
int dns_server_count = 0;

#define A 1 // 查询类型，表示由域名获得IPv4地址
#define CNAME 5
#define TXT 16
#define AAAA 28
#define MX 15
#define NS 2
#define SOA 6
#define PTR 12
#define SRV 33
#define ANY 255

void searchTypeName(int type, unsigned char* name)
{
    switch (type)
    {
    case A:
        strcpy(name, "A");
        break;
    case CNAME:
        strcpy(name, "CNAME");
        break;
    case TXT:
        strcpy(name, "TXT");
        break;
    case AAAA:
        strcpy(name, "AAAA");
        break;
    case MX:
        strcpy(name, "MX");
        break;
    case NS:
        strcpy(name, "NS");
        break;
    case SOA:
        strcpy(name, "SOA");
        break;
    case PTR:
        strcpy(name, "PTR");
        break;
    case SRV:
        strcpy(name, "SRV");
        break;
    case ANY:
        strcpy(name, "ANY");
        break;
    default:
        strcpy(name, "UNKNOWN");
        break;
    }
}

// 从www.baidu.com转换到3www5baidu3com
void ChangetoDnsNameFormat(unsigned char *dns, unsigned char *host)
{
    int lock = 0, i;
    strcat((char *)host, ".");
    for (i = 0; i < strlen((char *)host); i++)
    {
        if (host[i] == '.')
        {
            *dns++ = i - lock;
            for (; lock < i; lock++)
            {
                *dns++ = host[lock];
            }
            lock++;
        }
    }
    *dns++ = '\0';
}

int readDnsNameString(unsigned char *p, unsigned char *host, unsigned char *buf)
{
    int len = 0;
    int lock = 0, i = 0;
    while (*p != 0)
    {   
        if (*p == 0)
            break;
        else if (*p == 0xc0)
        {
            unsigned short name_pointer = ntohs(*(unsigned short *)p);
            if ((name_pointer & 0xc000) == 0xc000)
            {
                name_pointer = name_pointer & 0x3fff;
                readDnsNameString(buf + name_pointer, host + lock, buf);
            }
            else
            {
                readDnsNameString(p, host, buf);
            }
            return len + 2;
        }
        int num = *p++;
        len++;
        for (i = 0; i < num; i++)
        {
            host[lock++] = *p++;
            len++;
        }
        host[lock++] = '.';
    }
    host[lock] = '\0';
    return len;
}


// DNS报文首部, 这里使用了位域
struct DNS_HEADER
{
    unsigned short id;    // 会话标识
    // Flag
    unsigned char rd : 1; // 表示期望递归
    unsigned char tc : 1; // 表示可截断的
    unsigned char aa : 1; //  表示授权回答
    unsigned char opcode : 4;
    unsigned char qr : 1;    //  查询/响应标志，0为查询，1为响应
    unsigned char rcode : 4; // 应答码
    unsigned char cd : 1;
    unsigned char ad : 1;
    unsigned char z : 1;       // 保留值
    unsigned char ra : 1;      // 表示可用递归

    unsigned short q_count;    // 表示查询问题区域节的数量
    unsigned short ans_count;  // 表示回答区域的数量
    unsigned short auth_count; // 表示授权区域的数量
    unsigned short add_count;  // 表示附加区域的数量
};

// DNS报文中查询问题区域
struct QUESTION
{
    unsigned short qtype;  // 查询类型
    unsigned short qclass; // 查询类
};

typedef struct
{
    unsigned char *name;
    struct QUESTION *ques;
} QUERY;

// DNS报文中回答区域的常量字段
// 编译制导命令
#pragma pack(push, 1) // 保存对齐状态，设定为1字节对齐
struct R_DATA
{
    unsigned short type;     // 表示资源记录的类型
    unsigned short _class;   // 类
    unsigned int ttl;        // 表示资源记录可以缓存的时间
    unsigned short data_len; // 数据长度
};
#pragma pack(pop) // 恢复对齐状态

// DNS报文中回答区域的资源数据字段
struct RES_RECORD
{
    unsigned char *name;     // 资源记录包含的域名
    struct R_DATA *resource; // 资源数据
    unsigned char *rdata;
};

char replyCodeType[11][50] = {
    "No error condition",
    "Format error",
    "Server failure",
    "Name error",
    "Not Implemented",
    "Refused",
    "YXDomain",
    "YXRRSet",
    "NXRRSet",
    "NotAuth",
    "NotZone"
};

// 实现DNS查询功能
void ngethostbyname(unsigned char *host, int query_type, int class)
{
    unsigned char buf[65536], *qname, *reader;
    int i, j, stop, s;
    struct sockaddr_in a; // 地址
    // 回答区域、授权区域、附加区域中的资源数据字段
    struct RES_RECORD answers[20], auth[20], addit[20];
    struct sockaddr_in dest; // 地址
    struct DNS_HEADER *dns = NULL;
    struct QUESTION *qinfo = NULL;

    char typeName[10];
    searchTypeName(query_type, typeName);
    printf("Send %s DNS Search (%s, %s)\n", dns_servers, host, typeName);
    s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP); // 建立分配UDP套结字
    dest.sin_family = AF_INET;                        // IPv4
    dest.sin_port = htons(53);                        // 53号端口
    dest.sin_addr.s_addr = inet_addr(dns_servers); // DNS服务器IP

    dns = (struct DNS_HEADER *)&buf;
    /*设置DNS报文首部*/
    dns->id = (unsigned short)htons(getpid()); // id设为进程标识符
    dns->qr = 0;                               // 查询
    dns->opcode = 0;                           // 标准查询
    dns->aa = 0;                               // 不授权回答
    dns->tc = 0;                               // 不可截断
    dns->rd = 1;                               // 期望递归
    dns->ra = 0;                               // 不可用递归
    dns->z = 0;                                // 必须为0
    dns->ad = 0;
    dns->cd = 0;
    dns->rcode = 0;          // 没有差错
    dns->q_count = htons(1); // 1个问题
    dns->ans_count = 0;
    dns->auth_count = 0;
    dns->add_count = 0;

    // qname指向查询问题区域的查询名字段
    qname = (unsigned char *)&buf[sizeof(struct DNS_HEADER)];
    // 修改域名格式
    ChangetoDnsNameFormat(qname, host);
    // qinfo指向问题查询区域的查询类型字段
    qinfo = (struct QUESTION *)&buf[sizeof(struct DNS_HEADER) + (strlen((const char *)qname) + 1)];
    qinfo->qtype = htons(query_type);
    qinfo->qclass = htons(class);         // 查询类为1

    // 发送DNS请求报文
    if (sendto(s, (char *)buf, sizeof(struct DNS_HEADER) + (strlen((const char *)qname) + 1) + sizeof(struct QUESTION), 0, (struct sockaddr *)&dest, sizeof(dest)) < 0)
    {
        perror("Send failed!\n");
        return;
    }
    // printf("Send success!\n");

    // 接受DNS响应报文
    i = sizeof dest;
    int len = recvfrom(s, (char *)buf, 65536, 0, (struct sockaddr *)&dest, (socklen_t *)&i);
    if (len < 0)
    {
        perror("Get response failed!\n");
        return;
    }
    // printf("Get response successfully!\n");

    for (i = 0; i < (int)(len / 16) + 1; i++)
    {
        for (j = 0; j < 16; j++)
            printf("%02x ", buf[i * 16 + j]);
        printf("\t");
        for (j = 0; j < 16; j++)
            if (buf[i * 16 + j] >= 32 && buf[i * 16 + j] <= 128)
                printf("%c ", buf[i * 16 + j]);
            else
                printf(". ");
        printf("\n");
    }
    printf("\n");

    dns = (struct DNS_HEADER *)buf;
    printf("Transaction ID: %d\n", ntohs(dns->id));
    // 解析flag
    printf("Flag:\n");
    printf("\tResponce: %d\n", dns->qr);
    printf("\tOpcode: %d\n", dns->opcode);
    printf("\tAuthoritative: %d\n", dns->aa);
    printf("\tTruncated: %d\n", dns->tc);
    printf("\tRecursion desired: %d\n", dns->rd);
    printf("\tRecursion available: %d\n", dns->ra);
    printf("\tZ: %d\n", dns->z);
    printf("\tAnswer authenticated: %d\n", dns->ad);
    printf("\tNon-authenticated data: %d\n", dns->cd);
    printf("\tReply code: %d -> %s\n", dns->rcode, replyCodeType[dns->rcode]);
    printf(
        "Recv: %d question, %d answer, %d authority, %d additional\n", 
        ntohs(dns->q_count), ntohs(dns->ans_count), 
        ntohs(dns->auth_count), ntohs(dns->add_count)
    );
    // 将reader指向Answer报文的回答区域
    reader = &buf[sizeof(struct DNS_HEADER) + (strlen((const char *)qname) + 1) + sizeof(struct QUESTION)];
    // 解析Answer报文 
    for (i = 0; i < ntohs(dns->ans_count); i++)
    {
        printf("Answer %d:\n", i + 1);
        // 解析Name
        answers[i].name = (unsigned char *)malloc(256);
        readDnsNameString(reader, answers[i].name, buf);
        printf("\tName: %s\n", answers[i].name);
        // 指向回答区域的资源数据字段
        answers[i].resource = (struct R_DATA *)(reader + sizeof(short));
        printf("\tLength: %d\n", ntohs(answers[i].resource->data_len));
        printf("\tTTL: %d\n", ntohl(answers[i].resource->ttl));
        searchTypeName(ntohs(answers[i].resource->type), typeName);
        printf("\tType: %d -> %s\n", ntohs(answers[i].resource->type), typeName);
        // 指向回答区域的资源数据字段的数据字段
        unsigned char *data = reader + sizeof(short) + sizeof(struct R_DATA);
        if (ntohs(answers[i].resource->type) == A)
        {
            int ip = 0;
            char ip_str[20];
            for (j = 0; j < ntohs(answers[i].resource->data_len); j++)
                ip = (ip << 8) + data[j];
            sprintf(ip_str, "%d.%d.%d.%d", (ip >> 24) & 0xFF, (ip >> 16) & 0xFF, (ip >> 8) & 0xFF, ip & 0xFF);
            printf("\tIP: %s\n", ip_str);
        }
        else if (ntohs(answers[i].resource->type) == TXT)
        {
            // 指向回答区域的资源数据字段的数据字段
            answers[i].rdata = (unsigned char *)malloc(ntohs(answers[i].resource->data_len));
            for (j = 0; j < ntohs(answers[i].resource->data_len); j++)
            {
                answers[i].rdata[j] = data[j];
            }
            answers[i].rdata[j] = '\0';
            printf("\tTXT: %s\n", answers[i].rdata);
        }
        else if (ntohs(answers[i].resource->type) == CNAME)
        {
            // 解析CNAME
            answers[i].rdata = (unsigned char *)malloc(ntohs(answers[i].resource->data_len));
            readDnsNameString(data, answers[i].rdata, buf);
            printf("\tCName: %s\n", answers[i].rdata);
        }
        else if (ntohs(answers[i].resource->type) == SOA)
        {
            // 解析SOA
            answers[i].rdata = (unsigned char *)malloc(ntohs(answers[i].resource->data_len));
            for (j = 0; j < ntohs(answers[i].resource->data_len); j++)
                answers[i].rdata[j] = data[j];
            answers[i].rdata[j] = '\0';
            unsigned char *primaryNameServer = (unsigned char *)malloc(256);
            unsigned char *responsibleAuthorityMailbox = (unsigned char *)malloc(256);
            int l = readDnsNameString(data, primaryNameServer, buf);
            l += readDnsNameString(data + l, responsibleAuthorityMailbox, buf);
            printf("\tPrimary name server: %s\n", primaryNameServer);
            printf("\tResponsible authority mailbox: %s\n", responsibleAuthorityMailbox);
            int serialNumber = ntohs(*(unsigned int *)(data + l));
            int refreshInterval = ntohl(*(unsigned int *)(data + l + 4));
            int retryInterval = ntohl(*(unsigned int *)(data + l + 8));
            int expireLimit = ntohl(*(unsigned int *)(data + l + 12));
            int minimumTTL = ntohl(*(unsigned int *)(data + l + 16));
            printf("\tSerial number: %d\n", serialNumber);
            printf("\tRefresh interval: %d\n", refreshInterval);
            printf("\tRetry interval: %d\n", retryInterval);
            printf("\tExpire limit: %d\n", expireLimit);
            printf("\tMinimum TTL: %d\n", minimumTTL);
        }
        else if (ntohs(answers[i].resource->type) == NS)
        {
            // 解析NS
            answers[i].rdata = (unsigned char *)malloc(256);
            readDnsNameString(data, answers[i].rdata, buf);
            printf("\tName server: %s\n", answers[i].rdata);
        }
        // 指向下一个回答区域
        reader = reader + sizeof(short) + sizeof(struct R_DATA) + ntohs(answers[i].resource->data_len);
    }
    // 授权区域
    for (i = 0; i < ntohs(dns->auth_count); i++)
    {
        printf("Authority %d:\n", i + 1);
        int nameLen = 2;
        auth[i].name = (unsigned char *)malloc(256);
        if (reader[0] == 0) {
            nameLen = 1;
            strcpy(auth[i].name, "root");
        } else
            readDnsNameString(reader, auth[i].name, buf);
        printf("\tName: %s\n", auth[i].name);
        auth[i].resource = (struct R_DATA *)(reader + nameLen);
        printf("\tLength: %d\n", ntohs(auth[i].resource->data_len));
        printf("\tTTL: %d\n", ntohl(auth[i].resource->ttl));
        searchTypeName(ntohs(auth[i].resource->type), typeName);
        printf("\tType: %d -> %s\n", ntohs(auth[i].resource->type), typeName);
        unsigned char *data = reader + nameLen + sizeof(struct R_DATA);
        if (ntohs(auth[i].resource->type) == NS)
        {
            auth[i].rdata = (unsigned char *)malloc(256);
            readDnsNameString(data, auth[i].rdata, buf);
            printf("\tName server: %s\n", auth[i].rdata);
        }
        else if (ntohs(auth[i].resource->type) == SOA)
        {
            auth[i].rdata = (unsigned char *)malloc(ntohs(auth[i].resource->data_len));
            for (j = 0; j < ntohs(auth[i].resource->data_len); j++)
                auth[i].rdata[j] = data[j];
            auth[i].rdata[j] = '\0';
            unsigned char *primaryNameServer = (unsigned char *)malloc(256);
            unsigned char *responsibleAuthorityMailbox = (unsigned char *)malloc(256);
            int l = readDnsNameString(data, primaryNameServer, buf);
            l += readDnsNameString(data + l, responsibleAuthorityMailbox, buf);
            printf("\tPrimary name server: %s\n", primaryNameServer);
            printf("\tResponsible authority mailbox: %s\n", responsibleAuthorityMailbox);
            int serialNumber = ntohs(*(unsigned int *)(data + l));
            int refreshInterval = ntohl(*(unsigned int *)(data + l + 4));
            int retryInterval = ntohl(*(unsigned int *)(data + l + 8));
            int expireLimit = ntohl(*(unsigned int *)(data + l + 12));
            int minimumTTL = ntohl(*(unsigned int *)(data + l + 16));
            printf("\tSerial number: %d\n", serialNumber);
            printf("\tRefresh interval: %d\n", refreshInterval);
            printf("\tRetry interval: %d\n", retryInterval);
            printf("\tExpire limit: %d\n", expireLimit);
            printf("\tMinimum TTL: %d\n", minimumTTL);
        }
        reader = reader + nameLen + sizeof(struct R_DATA) + ntohs(auth[i].resource->data_len);
    }
    return;
}


int main(int argc, char *argv[])
{
    unsigned char hostname[100] = "version.bind";
    unsigned char dns_servername[100] = "114.114.114.114";
    int type = ANY, class = ANY;
    if (argc > 1)
        strcpy(dns_servername, argv[1]);
    if (argc > 2)
        strcpy(hostname, argv[2]);
    if (argc > 3)
        type = atoi(argv[3]);
    if (argc > 4)
        class = atoi(argv[4]);
    strcpy(dns_servers, dns_servername);
    ngethostbyname(hostname, type, class);
    return 0;
}
```

