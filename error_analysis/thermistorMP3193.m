clc
close all

% Author: Luke Denn
% Goal: create a temperature-resistance curve for
% for the thermistor in the TD-720 Controller

R = [146735
138447
130677
123390
116554
110138
104113
98454
93137
88138
83438
79016
74855
70938
67249
63773
60498
57410
54498
51750
49157
46709
44397
42213
40150
38199
36354
34608
32957
31394
29914
28512
27183
25925
24731
23600
22526
21508
20541
19623
18751
17923
17136
16388
15676
15000
14356
13744
13161
12606
12078
11574
11095
10637
10202
9786
9389
9011
8650
8306
7976
7662
7362
7075
6801
6539
6289
6049
5820
5600
5391
5190
4997
4813
4637
4467
4305
4150
4001
3858
3721
3590
3464
3343
3227
3115
3008
2905
2806
2711
2620
2532
2448
2367
2288
2213
2141
2072
2005
1940
1878
1818
1761
1705
1652
1601
1551
1503
1457
1412
1369
1328
1288
1250
1212
1176
1142
1108
1076
1045
1014];

T = -20:100;
T = T';

plot(T,log(R)); hold on
ylabel('log(R Ohms)')
xlabel('T degrees C')


%% Linear Fit
f = fit(T,log(R),'poly1')
plot(f)
set(gca,'YScale','log')
title('-20 to 100 degrees celcius')


%% 25-50 degrees celcius
%index = 46:71; for 25 degrees celcius to 50 degrees celcius
% in T and R arrays
% should be more accurate for our needs
figure(2)
ylabel('log(R Ohms)')
xlabel('T degrees C')
hold on; set(gca,'YScale','log')
plot(T(46:71),log(R(46:71)));
f2 = fit(T(46:71),log(R(46:71)),'poly1')
plot(f2)
title('25 to 50 degrees celcius')
