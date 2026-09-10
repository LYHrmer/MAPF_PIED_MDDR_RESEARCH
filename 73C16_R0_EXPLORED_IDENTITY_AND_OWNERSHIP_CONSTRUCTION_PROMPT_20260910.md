# 73C16 固定 R0 EXPLORED 身份与对象归属：独立窄建设题

NO-SKILL / CONSTRUCTIVE / NONBALLOT，禁止工具、skills、搜索、代码/伪代码、构建、测试、运行、仿真、参数赋值、数据载荷。仅根据下列实际固定源码作纸面分析，末尾 END-C16。此题与 C14 数值精度不同，不重启或续写旧题。只交一个最小、可审查的修订包，不扩成全仓审计或宣布整个源通过。

固定 R0 为 YueZhang-studyuse/LMAPF-delay，commit 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357。下列片段由根子代理本次通过固定 ref API 取得并亲读；带原行号，不是新代码。对象：src/MAPF-LNS2/src/lacam2/planner.cpp，blob 4f46f988d2c16f09c5a6f65bb9cd70e8e01aa483，SHA256 8d2fa9131f0691b109a00dd6267b3b48f80df7778643daeb806ff82e20fe2789，19115 bytes/615 LF；inc/MAPF-LNS2/inc/lacam2/planner.hpp，blob 48ec12187373e87d6a233bfebea5eaf8b26c9304，SHA256 8e7c6b7221828ef17a73730a3a33c39d5fcc9ccd9f73a6697c7434162ae7312c，3850/132。直接键依赖 graph.hpp，blob bdf87cf5a1b911c039ebcf10374ddf317086fbd4，SHA256 166b3ecbe68e7ddcd549504044a3c47cc3abb9ca98653b8639a654607480daee，1699/61；graph.cpp，blob fb8ab481d5b1e3a959a18b826fd5919b69772e7e，SHA256 7bdb71a22dbdf6df873370c20173f0ef9ab97c34fbb649f222c7bcb9fa2813a0，4405/185。原 URL 为 https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/ 加相应完整路径。

背景只用于判定修订代价：当前研究仍 HOLD/NO-GO-IMPLEMENT/NO-GO-MAIN-EXPERIMENT。既有路线是修订版 pure LaCAM、ALWAYS_ADVANCE/FAIL_STOP_SOURCE：正常、内部继续域合格的源调用即使外部计划软拒收也保留内部源状态；真实异常/源损坏 fail-stop，不伪装成正常拒收重试。源内部调用的 Planner 本来为单次求解局部对象，外层持续源状态不等于复用每次 HNode 搜索图。此前根已登记 H_goal 空值先于日志/回溯的检查、单已知任务目标解析、puller 行与交换循环更新等纸面修订，但本题未亲核那些后继全文，以下仍精确是固定原样 R0。不得借那些修订宣称身份/所有权已经正确；不允许靠进程退出吞掉本次原析构成本。

题目请独立核：find 的 (C_new,num_reached) 与新插入 L232 的 (H->C,H->reach_goal) 是什么状态？查找 flags 应来自哪里、能否只换插入键？RCEqual/Hash 是否遵守同一身份？哪些节点会从 EXPLORED 析构入口失联？已有节点被 OPEN/neighbor 多次引用是否就等于重复 delete？已 pop 的 L 在两处 deadline break 的真实所有权是什么？请区分确证控制流问题、条件反例、无法证明的具体运行 UB，不凭名字或超时就声称 double-free。

planner.cpp 原文：LNode/HNode 构造及 HNode 析构
```text
3: LNode::LNode(LNode* parent, uint i, Vertex* v)
4: : who(), where(), depth(parent == nullptr ? 0 : parent->depth + 1)
5: {
6:     if (parent != nullptr) 
7:     {
8:         who = parent->who;
9:         who.push_back(i);
10:         where = parent->where;
11:         where.push_back(v);
12:     }
13: }
14: 
15: uint HNode::HNODE_CNT = 0;
16: 
17: // for high-level
18: //HNode::HNode(const Config& _C, DistTable& D, HNode* _parent, const uint _g, const uint _h)
19: HNode::HNode(const Config& _C, const Instance& I, HNode* _parent, const uint _g, const uint _h)
20:     : C(_C),
21:       parent(_parent),
22:       neighbor(),
23:       g(_g),
24:       h(_h),
25:       f(g + h),
26:       priorities(C.size()),
27:       order(C.size(), 0),
28:       search_tree(std::queue<LNode*>())
29: {
30:     ++HNODE_CNT;
31:     search_tree.push(new LNode());
32:     const auto N = C.size();
33: 
34:     //init reach goal size
35:     reach_goal.resize(N);
36: 
37:     // update neighbor
38:     if (parent != nullptr) 
39:         parent->neighbor.insert(this);
40: 
41:     // set priorities
42:     if (parent == nullptr) 
43:     {
44:         // initialize
45:         for (uint i = 0; i < N; ++i)
46:         {
47:           priorities[i] = (float)i/N;
48:           reach_goal[i] = 0; //do not reach goal at the start stage
49:         }
50:         depth = 0;
51:     } 
52:     else 
53:     {
54:         depth = parent->depth+1;
55:         curr_time = parent->curr_time + 1;
56:         // dynamic priorities, akin to PIBT
57:         for (size_t i = 0; i < N; ++i) 
58:         { 
59:             if (parent->reach_goal[i] > 0) //reached goal before
60:             {
61:                 reach_goal[i] = parent->reach_goal[i];
62:                 num_agent_reached++;
63:                 //get current goal
64:                 auto curr_goal = I.env->goal_locations[i][reach_goal[i]].first;
65:                 // if (I.getAllpairDistance(dummy_goal, C[i]->index) == 0) //also reached dummy goal
66:                 // {
67:                 if (I.getAllpairDistance(curr_goal,C[i]->index) == 0)
68:                     priorities[i] = parent->priorities[i] - (int)parent->priorities[i];
69:                 //}
70:             }
71:             else
72:             {
73:                 auto goal_index = I.env->goal_locations[i][0].first; //current we only consider plan for the first goal
74:                 if (I.getAllpairDistance(goal_index, C[i]->index) == 0) //current timestep arrive the real goal
75:                 {
76:                     reach_goal[i]++;
77:                     num_agent_reached++;
78:                     priorities[i] = parent->priorities[i] - (int)parent->priorities[i];
79:                 }
80:                 else //still not arrived
81:                 {
82:                     priorities[i] = parent->priorities[i] + 1;
83:                 }
84:             }
85:         }
86:     }
87: 
88:   // set order
89:   std::iota(order.begin(), order.end(), 0);
90:   std::sort(order.begin(), order.end(),
91:             [&](uint i, uint j) { return priorities[i] > priorities[j]; });
92: }
93: 
94: HNode::~HNode()
95: {
96:   while (!search_tree.empty()) {
97:     delete search_tree.front();
98:     search_tree.pop();
99:   }
100: }
```

planner.hpp 原文：Agent/LNode/HNode 与 Planner 字段/接口
```text
17: // PIBT agent
18: struct LACAMAgent {
19:   const uint id;
20:   Vertex* v_now;   // current location
21:   Vertex* v_next;  // next location
22:   int goal_index = 0; //for reach goal disappear
23:   int curr_timestep = 0;
24:   LACAMAgent(uint _id) : id(_id), v_now(nullptr), v_next(nullptr) {}
25: };
26: using LACAMAgents = std::vector<LACAMAgent*>;
27: 
28: // low-level node
29: struct LNode {
30:   std::vector<uint> who;
31:   Vertices where;
32:   const uint depth;
33:   LNode(LNode* parent = nullptr, uint i = 0,
34:         Vertex* v = nullptr);  // who and where
35: };
36: 
37: // high-level node
38: struct HNode {
39:   static uint HNODE_CNT;  // count #(high-level node)
40:   const Config C;
41: 
42:   // tree
43:   HNode* parent;
44:   std::set<HNode*> neighbor;
45: 
46:   // costs
47:   uint g;        // g-value (might be updated)
48:   const uint h;  // h-value
49:   uint f;        // g + h (might be updated)
50: 
51:   int curr_time = 0;
52: 
53:   //reached goal count
54:   //std::vector<bool> reach_goal;
55:   std::vector<int> reach_goal;
56: 
57:   int num_agent_reached = 0;
58: 
59:   // for low-level search
60:   std::vector<float> priorities;
61:   std::vector<uint> order;
62:   std::queue<LNode*> search_tree;
63: 
64:   int depth = 0;
65: 
66:   // HNode(const Config& _C, DistTable& D, HNode* _parent, const uint _g,
67:   //       const uint _h);
68:   HNode(const Config& _C, const Instance& I, HNode* _parent, const uint _g,
69:         const uint _h);
70:   ~HNode();
71: };
72: using HNodes = std::vector<HNode*>;
73: 
74: struct Planner {
75:   const Instance& instance;
76:   const LACAMInstance* ins;
77:   const Deadline* deadline;
78:   std::mt19937* MT;
79:   const int verbose;
80: 
81:   // hyper parameters
82:   const Objective objective;
83:   const float RESTART_RATE;  // random restart
84: 
85:   // solver utils
86:   const uint N;       // number of agents
87:   const uint V_size;  // number o vertices
88:   //DistTable D; //use my all pair heuristic
89:   uint loop_cnt;      // auxiliary
90: 
91:   int commit_window = 1;
92: 
93:   // used in PIBT
94:   std::vector<std::array<Vertex*, 5> > C_next;  // next locations, used in PIBT
95:   std::vector<float> tie_breakers;              // random values, used in PIBT
96:   LACAMAgents A;
97:   LACAMAgents occupied_now;                          // for quick collision checking
98:   LACAMAgents occupied_next;                         // for quick collision checking
99: 
100:   Planner(const Instance& _instance, const LACAMInstance* _ins, const Deadline* _deadline, std::mt19937* _MT,
101:           const int _verbose = 0,
102:           // other parameters
103:           const Objective _objective = OBJ_NONE,
104:           const float _restart_rate = 0.001);
105:   ~Planner();
106:   Solution solve(std::string& additional_info);
107:   void expand_lowlevel_tree(HNode* H, LNode* L);
108:   void rewrite(HNode* H_from, HNode* T, HNode* H_goal,
109:                std::stack<HNode*>& OPEN);
110:   uint get_edge_cost(const Config& C1, const Config& C2);
111:   uint get_edge_cost(HNode* H_from, HNode* H_to);
112:   uint get_h_value(const Config& C);
113:   bool get_new_config(HNode* H, LNode* L);
114:   bool funcPIBT(LACAMAgent* ai);
115: 
116:   // swap operation
```

planner.cpp 原文：solve 与 rewrite
```text
127: Solution Planner::solve(std::string& additional_info)
128: {
129:     // setup agents
130:     for (auto i = 0; i < N; ++i) A[i] = new LACAMAgent(i);
131: 
132:     // setup search
133:     auto OPEN = std::stack<HNode*>();
134:     //auto EXPLORED = std::unordered_map<Config, HNode*, ConfigHasher>();
135:     auto EXPLORED = std::unordered_map<pair<Config,vector<int>>, HNode*, RConfigHasher, RCEqual>();
136:     // insert initial node, 'H': high-level node
137:     auto H_init = new HNode(ins->starts, instance, nullptr, 0, get_h_value(ins->starts));
138:     OPEN.push(H_init);
139:     //EXPLORED[H_init->C] = H_init;
140:     EXPLORED[make_pair(H_init->C, H_init->reach_goal)] = H_init;
141: 
142:     std::vector<Config> solution;
143:     auto C_new = Config(N, nullptr);  // for new configuration
144:     HNode* H_goal = nullptr;          // to store goal node
145:     HNode* curr_best = nullptr;
146: 
147:     // DFS
148:     while (!OPEN.empty() && !is_expired(deadline)) 
149:     {
150:         // do not pop here!
151:         auto H = OPEN.top();  // high-level node
152:         // low-level search end search tree refers to constraint tree
153:         if (H->search_tree.empty()) 
154:         {
155:             OPEN.pop();
156:             continue;
157:         }
158: 
159: 
160:         //record the current best, in case no solution found
161:         if (curr_best == nullptr)
162:             curr_best = H;
163:         else
164:         {
165:             if (curr_best->num_agent_reached < H->num_agent_reached)
166:                 curr_best = H;
167:             if (curr_best->num_agent_reached == H->num_agent_reached && curr_best->depth < H->depth)
168:                 curr_best = H;
169:         }
170: 
171:         // check goal condition -- reach goal once
172:         //should all reached the current goal and after that reach the dummy goal
173:         if (H_goal == nullptr) 
174:         {
175:             if (H->num_agent_reached == ins->N)
176:             {
177:                 H_goal = H;
178:                 break;
179:             }
180:         }
181: 
182:         // create successors at the low-level search
183:         auto L = H->search_tree.front();
184:         H->search_tree.pop();
185:         expand_lowlevel_tree(H, L); //generate constraint 
186: 
187:         if (is_expired(deadline)) break;
188: 
189: 
190:         // create successors at the high-level search
191:         const auto res = get_new_config(H, L);
192: 
193:         if (is_expired(deadline)) break;
194: 
195:         delete L;  // free
196:         if (!res) 
197:         {
198:             continue;
199:         }
200: 
201: 
202:         vector<int> num_reached;
203:         num_reached.resize(A.size());
204:         // create new configuration
205:         for (auto a : A) 
206:         {
207:           C_new[a->id] = a->v_next;
208:           num_reached[a->id] = a->goal_index;
209:         }
210: 
211:         // check explored list
212:         //const auto iter = EXPLORED.find(C_new);
213:         const auto iter = EXPLORED.find(make_pair(C_new,num_reached));
214:         if (iter != EXPLORED.end()) 
215:         {
216:             // case found
217:             rewrite(H, iter->second, H_goal, OPEN);
218:             // re-insert or random-restart
219:             auto H_insert = (MT != nullptr && get_random_float(MT) >= RESTART_RATE)
220:                                 ? iter->second
221:                                 : H_init;
222:             if (H_goal == nullptr || H_insert->f < H_goal->f) 
223:             {
224:                 OPEN.push(H_insert);
225:             }
226:         } 
227:         else 
228:         {
229:             // insert new search node
230:             const auto H_new = new HNode(C_new, instance, H, H->g + get_edge_cost(H->C, C_new), get_h_value(C_new));
231:             //EXPLORED[H_new->C] = H_new;
232:             EXPLORED[make_pair(H->C,H->reach_goal)] = H_new;
233:             if (H_goal == nullptr || H_new->f < H_goal->f) 
234:             {
235:                 OPEN.push(H_new);
236:             }
237:         }
238:     }
239: 
240:     if (H_goal == nullptr)
241:     {
242:       H_goal = curr_best;
243:     }
244: 
245:     cout<<"num of goal reached "<<H_goal->num_agent_reached<<endl;
246: 
247:     // backtrack
248:     if (H_goal != nullptr) 
249:     {
250:         auto H = H_goal;
251:         while (H != nullptr) 
252:         {
253:             solution.push_back(H->C);
254:             H = H->parent;
255:         }
256:         std::reverse(solution.begin(), solution.end());
257:     }
258: 
259:     // memory management
260:     for (auto a : A) delete a;
261:     for (auto itr : EXPLORED) delete itr.second;
262: 
263:     return solution;
264: }
265: 
266: void Planner::rewrite(HNode* H_from, HNode* H_to, HNode* H_goal,
267:                       std::stack<HNode*>& OPEN)
268: {
269:     // update neighbors
270:     H_from->neighbor.insert(H_to);
271: 
272:     // Dijkstra update
273:     std::queue<HNode*> Q({H_from});  // queue is sufficient
274:     while (!Q.empty()) 
275:     {
276:         auto n_from = Q.front();
277:         Q.pop();
278:         for (auto n_to : n_from->neighbor) 
279:         {
280:             auto g_val = n_from->g + get_edge_cost(n_from->C, n_to->C);
281:             if (g_val < n_to->g) 
282:             {
283:                 if (n_to == H_goal)
284:                     solver_info(1, "cost update: ", n_to->g, " -> ", g_val);
285:                 n_to->g = g_val;
286:                 n_to->f = n_to->g + n_to->h;
287:                 n_to->parent = n_from;
288:                 Q.push(n_to);
289:                 if (H_goal != nullptr && n_to->f < H_goal->f) OPEN.push(n_to);
290:             }
291:         }
292:     }
293: }
```

planner.cpp 原文：本次用到的费用函数、L 子树扩展与 get_new_config
```text
295: uint Planner::get_edge_cost(const Config& C1, const Config& C2) //comment because we only use lacam for one shot
296: {
297:     return 1; 
298: }
299: 
300: uint Planner::get_edge_cost(HNode* H_from, HNode* H_to)
301: {
302:     return get_edge_cost(H_from->C, H_to->C);
303: }
304: 
305: uint Planner::get_h_value(const Config& C) //commment due to only need one shot at this moment
306: {
307:     uint cost = 0;
308:     return cost;
309: }
310: 
311: void Planner::expand_lowlevel_tree(HNode* H, LNode* L)
312: {
313:     if (L->depth >= N) return; //prohibt each agent at one depth, so max is the number of agent
314:     const auto i = H->order[L->depth];
315:     auto C = H->C[i]->neighbor;
316:     C.push_back(H->C[i]);
317:     // randomize
318:     if (MT != nullptr) std::shuffle(C.begin(), C.end(), *MT); //random the order (neighbor)
319:     // insert
320:     for (auto v : C) H->search_tree.push(new LNode(L, i, v));
321: }
322: 
323: bool Planner::get_new_config(HNode* H, LNode* L)
324: {
325:     // setup cache
326:     for (auto a : A) 
327:     {
328:         // clear previous cache
329:         if (a->v_now != nullptr && occupied_now[a->v_now->id] == a) 
330:         {
331:             occupied_now[a->v_now->id] = nullptr;
332:         }
333:         if (a->v_next != nullptr) 
334:         {
335:             occupied_next[a->v_next->id] = nullptr;
336:             a->v_next = nullptr;
337:         }
338:         //clear previous reached goal flag
339:         a->goal_index = 0;
340:         a->curr_timestep = 0;
341: 
342:         // set occupied now
343:         a->v_now = H->C[a->id];
344:         a->curr_timestep = H->curr_time;
345: 
346:         a->goal_index = H->reach_goal[a->id];
347: 
348:         if (H->depth < commit_window || a->goal_index == 0) //cannot reach goal before window
349:         {
350:             occupied_now[a->v_now->id] = a;
351:         }
352:         if (a->goal_index > 0 && H->depth >= commit_window)
353:         {
354:             a->v_next = a->v_now;
355:         }
356:     }
357: 
358:     // add constraints
359:     for (uint k = 0; k < L->depth; ++k) 
360:     {
361:         const auto i = L->who[k];        // agent
362:         const auto l = L->where[k]->id;  // loc
363: 
364:         // check vertex collision
365:         if (occupied_next[l] != nullptr) return false;
366:         // check swap collision
367:         auto l_pre = H->C[i]->id;
368:         if (occupied_next[l_pre] != nullptr && occupied_now[l] != nullptr &&
369:             occupied_next[l_pre]->id == occupied_now[l]->id)
370:             return false;
371:         // set occupied_next
372:         A[i]->v_next = L->where[k];
373:         
374:         occupied_next[l] = A[i];
375: 
376:     }
377: 
378:     // perform PIBT
379:     for (auto k : H->order) 
380:     {
381:         if (is_expired(deadline)) return false; //timeout
382: 
383:         auto a = A[k];
384:         if (a->v_next == nullptr && !funcPIBT(a))
385:         {
386:             return false;  // planning failure
387:         }
388:     }
389: 
390:     return true;
391: }
```

补充实际全文核验：该 planner.cpp 中 goal_index 的赋值点在上述 get_new_config 清零与复制 H->reach_goal；后面的 funcPIBT/swap 中读取这些值，不在首达新 C 时回写它。不要把这个旧字段名自动解释为“已经是新 HNode 的 flags”。本题不读取任何地图/任务配置或实例载荷。

graph.hpp 原文（完整直接 key 定义）
```text
30: bool is_same_config(
31:     const Config& C1,
32:     const Config& C2);  // check equivalence of two configurations
33: 
34: // hash function of configuration
35: // c.f.
36: // https://stackoverflow.com/questions/10405030/c-unordered-map-fail-when-used-with-a-vector-as-key
37: struct ConfigHasher {
38:   uint operator()(const Config& C) const;
39: };
40: 
41: struct RConfigHasher {
42:   uint operator()(const std::pair<Config, std::vector<int> > &RC) const;
43: };
44: 
45: struct RCEqual
46: {
47:   bool operator()(const std::pair<Config, std::vector<int> > &RC1, const std::pair<Config, std::vector<int> > &RC2) const
48:   {
49:     if (!is_same_config(RC1.first, RC2.first))
50:       return false;
51:     for (int i = 0; i < RC2.first.size(); i++)
52:     {
53:       if (RC2.second[i] != RC2.second[i])
54:         return false;
55:     }
56:     return true;
57:   }
58: };
59: 
60: std::ostream& operator<<(std::ostream& os, const Vertex* v);
61: std::ostream& operator<<(std::ostream& os, const Config& config);
```

graph.cpp 原文（完整同配置与组合散列函数）
```text
140: bool is_same_config(const Config& C1, const Config& C2)
141: {
142:   const auto N = C1.size();
143:   for (size_t i = 0; i < N; ++i) {
144:     if (C1[i]->id != C2[i]->id) return false;
145:   }
146:   return true;
147: }
174: uint RConfigHasher::operator()(const std::pair<Config, std::vector<int> > &RC) const
175: {
176:   auto C = RC.first;
177:   uint hash = C.size();
178:   int index = 0;
179:   for (auto& v : C) 
180:   {
181:     hash ^= v->id*(int(RC.second[index]) + 1) + 0x9e3779b9 + (hash << 6) + (hash >> 2);
182:     index++;
183:   }
184:   return hash;
185: }
```

本代理另亲读 C++ 工作草案 https://eel.is/c++draft/unord.req 的 [unord.req.general] p.3/5/6：Pred 应定义键等价关系，等价键须有同一 hash；unordered_map 支持唯一键。这是维护者发布的工作草案文本，不是本机标准库绑定或运行证据。

请最终给四项即可：
1. 用原行号给最多三个关键构造，明确分开身份错误、资源失联和实际未运行的 UB/算法保证；如“重复所有权”不成立请直接纠正。
2. 选择一套最小纸面修改：新 flags 计算/键发布必须如何一致；索引与唯一对象归属如何分离；构造中 parent->neighbor.insert(this) 的部分构造/失败责任；在两处 deadline、异常、正常回溯后的单次销毁和 A/cache 清理顺序。不可实现或给伪代码。
3. 哪些改动改变搜索行为/随机消耗/截止结果，哪些只是清理；为什么不能凭 key 修正证明全部 LaCAM 正确性。特别核 rewrite 只改 g/f/parent，未同步 depth/curr_time/priorities/reach_goal，以及状态合并的前提，但不无限递归新算法设计。
4. AA 正常继续域、源失败及 D/R/E0 同源同费如何登记。所有新增 flags 判断/索引/登记/构造失败/GC/析构都付费，不能把源修复收益归 D；未知留下确切接口而不是泛化为全源 UNKNOWN。

不要把上文描述当成预定结论；若你选择保留某处原文请给具体理由。没有实际调用或运行证据就不得声称某个载荷触发 UB。末尾 END-C16。

