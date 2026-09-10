# 73C15：固定R0目标索引与单个已知任务的建设题

2026-09-10，根/root。全新有界NO-SKILL/CONSTRUCTIVE/NONBALLOT，不是C12重试或C14精度题。只读本提示，不访问工具、网络、文件、MCP、任何skill/slash。仅给数学/语义文字，不生成代码、伪代码、配置、实验载荷、参数数值/默认/范围或实验结果，不给PASS/GO。H、T_delay、B_CAL、B_max、B*、P_active、density N原义未赋值。当前HOLD，六门2 PASS/3 UNKNOWN/1 FAIL。

当前73固定输入ab0283a5ef6fb9b3a408f0d453fb763340f9241b01a63928851ceb5ddef48939，181390/583。内部源为固定R0 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357修复纯LACAM / ALWAYS_ADVANCE / FAIL_STOP_SOURCE；外部H19使用自己的ECBS，不可用弱对照掩盖内部源无定义。当前已明确隔离同步入口、第五堆>=改为>及空H_goal首次读取前的失败分流；这些是纸面源码差异，未实现。PRE_COMMIT_SHAPE在plan返回后、原commit清容器之前检查；源无输出形状即会话停止，不自动clearAll重试，正常软STALE保合格源历史。完整源定义域仍未闭。

任务输入只能来自已付TASK知识和原PROJECT：PROJECT从实际已知合法分配队列中预测消耗旧承诺访问，不能制造未来任务、复制目标作填充或把当前位置当伪目标。若队列空，原稿给NO_INPUT/HOLD并保留全roster与真实世界服务；队列非空并不保证有两项。每次TASK_SERVICE真实环境完成最多一个队首，visited/计划预测不计Q。各臂同规则，各自合法已知剩余任务可不同；不能运行后筛掉某个臂不够两项的block。

本题根新源观察：HNode reach_goal每个分量根为0；后继parent>0只复制，parent==0才可能++，其余保持0。Planner::get_new_config把它复制给A.goal_index；本对象完整标识符定位无其它改写。故在合法对象下它是0/1旗标而非任意任务序列下标。HNode(parent>0)、funcPIBT与swap读取env目标index1。LACAMInstance(SharedEnvironment*)只把每agent队首放入ins.goals，不扩写env队列；Instance::prepareDummy写独立dummy_goals，runLACAM2的update_dummygoals已注释，所以它们不能替缺失第二项背书。根正比较可取路线，不预选“所有agent必须两任务”作为整个研究的较小成功域。

请在下列原句与合同下：
1. 独立核0/1范围、单任务缺口及受影响读点，区分数组定义域、原启发式含义与完整算法正确性。
2. 给一套明确的、尽量保留标准single-known-goal LMAPF能力的最小来源修订；不要只写“加bounds check”。可讨论“缺第二项时，以同一已交付第一任务的既有目标顶点作为已访问agent的终端引导，不新增/重复task实例、不改reach_goal、不推真实完成、不额外append WAIT；若第二项确实已知就保原第二项引导”这个可被反驳候选，但无需接受。明确它是否改变原提议/搜索/随机消费/费用及与已修复R0的身份关系；不能声称原样等价。
3. 指出swap中的puller_goal实际读pusher行，是否应与本题一起明示更正为puller自己的合法目标，还是保其原语义并独立登记。不要由变量名推整算法正确性；用前后具体字段说明理由。源所见原句包含影子局部变量问题，可指出但不要递归全源审计或扩成无限修补计划。
4. 至多一个合法符号反例/不利情形，说明你选的规则仍不保吞吐/完备/真实服务，给完整费用与失败、继续域合同。只要求一份可审核建设方案，不给最终源码资格通过，也不让当前路线成为唯一选项。以END-C15单独结尾。

以下固定源窗口由根直接GitHub API取得，planner.cpp原blob4f46f988d2c16f09c5a6f65bb9cd70e8e01aa483；不是实现指令，原源码中的常量只是身份。未给的全源不能宣称本题读过。

固定 planner.cpp L19–92
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

固定 planner.cpp L323–390
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

固定 planner.cpp L393–471
393: bool Planner::funcPIBT(LACAMAgent* ai)
394: {
395:     const auto i = ai->id;
396:     const auto K = ai->v_now->neighbor.size();
397: 
398:     // get candidates for next locations
399:     for (auto k = 0; k < K; ++k) 
400:     {
401:         auto u = ai->v_now->neighbor[k];
402:         C_next[i][k] = u;
403:         if (MT != nullptr)
404:             tie_breakers[u->id] = get_random_float(MT);  // set tie-breaker
405:     }
406:     C_next[i][K] = ai->v_now;
407: 
408:     LACAMAgent* swap_agent = nullptr;
409: 
410: 
411:     int goal_loc =instance.env->goal_locations[i][ai->goal_index].first;
412:     // ai->reached_goal ? instance.getDummyGoals()[i] : instance.env->goal_locations[i][0].first;
413:     //sort
414:     std::sort(C_next[i].begin(), C_next[i].begin() + K + 1,
415:               [&](Vertex* const v, Vertex* const u) 
416:               {
417:                   // return D.get(i, v) + tie_breakers[v->id] <
418:                   //       D.get(i, u) + tie_breakers[u->id];
419:                   return instance.getAllpairDistance(goal_loc,v->index) + tie_breakers[v->id] <
420:                           instance.getAllpairDistance(goal_loc,u->index) + tie_breakers[u->id];
421:               });
422: 
423:     swap_agent = swap_possible_and_required(ai);
424: 
425:     if (swap_agent != nullptr)
426:     {
427:       std::reverse(C_next[i].begin(), C_next[i].begin() + K + 1);
428:     }
429:     //cout<<"operations "<<K<<endl;
430:       
431:     // main operation
432:     for (auto k = 0; k < K + 1; ++k) 
433:     {
434:         auto u = C_next[i][k];
435: 
436: 
437:         // avoid vertex conflicts
438:         if (occupied_next[u->id] != nullptr) 
439:         {
440:             continue;
441:         }
442: 
443: 
444:         auto& ak = occupied_now[u->id];
445: 
446:         // avoid swap conflicts
447:         if (ak != nullptr && ak->v_next == ai->v_now) continue;
448: 
449:         // reserve next location
450:         occupied_next[u->id] = ai;
451:         ai->v_next = u;
452: 
453:         // priority inheritance
454:         if (ak != nullptr && ak != ai && ak->v_next == nullptr && !funcPIBT(ak))
455:           continue;
456: 
457:         // success to plan next one step
458:         // pull swap_agent when applicable
459:         if (k == 0 && swap_agent != nullptr && swap_agent->v_next == nullptr &&
460:             occupied_next[ai->v_now->id] == nullptr) 
461:         {
462:             swap_agent->v_next = ai->v_now;
463:             occupied_next[swap_agent->v_next->id] = swap_agent;
464:         }
465:         return true;
466:     }
467: 
468:     // failed to secure node
469:     occupied_next[ai->v_now->id] = ai;
470:     ai->v_next = ai->v_now;
471:     return false;

固定 planner.cpp L474–569
474: LACAMAgent* Planner::swap_possible_and_required(LACAMAgent* ai)
475: {
476:     const auto i = ai->id;
477:     // ai wanna stay at v_now -> no need to swap
478:     if (C_next[i][0] == ai->v_now) return nullptr;
479: 
480:     // usual swap situation, c.f., case-a, b
481:     auto aj = occupied_now[C_next[i][0]->id];
482:     if (aj != nullptr && aj->v_next == nullptr &&
483:         is_swap_required(ai->id, aj->id, ai->v_now, aj->v_now) &&
484:         is_swap_possible(aj->v_now, ai->v_now)) 
485:     {
486:         return aj;
487:     }
488: 
489:     // for clear operation, c.f., case-c
490:     for (auto u : ai->v_now->neighbor) 
491:     {
492:         auto ak = occupied_now[u->id];
493:         if (ak == nullptr || C_next[i][0] == ak->v_now) continue;
494:         if (is_swap_required(ak->id, ai->id, ai->v_now, C_next[i][0]) &&
495:             is_swap_possible(C_next[i][0], ai->v_now)) 
496:         {
497:             return ak;
498:         }
499:     }
500: 
501:     return nullptr;
502: }
503: 
504: // simulate whether the swap is required
505: bool Planner::is_swap_required(const uint pusher, const uint puller,
506:                                Vertex* v_pusher_origin, Vertex* v_puller_origin)
507: {
508: 
509:     auto pusher_goal = instance.env->goal_locations[pusher][A[pusher]->goal_index].first;
510:     //A[pusher]->reached_goal ? instance.getDummyGoals()[pusher] : instance.env->goal_locations[pusher][0].first;
511:     auto puller_goal = instance.env->goal_locations[pusher][A[puller]->goal_index].first;
512:     //A[puller]->reached_goal ? instance.getDummyGoals()[puller] : instance.env->goal_locations[puller][0].first;
513:     if (pusher_goal == puller_goal)
514:     {
515:         return false; //no need to swap with same goal
516:     }
517:     
518:     auto v_pusher = v_pusher_origin;
519:     auto v_puller = v_puller_origin;
520:     int pusher_vpuller = instance.getAllpairDistance(pusher_goal,v_puller->index);
521:     //A[pusher]->reached_goal ? instance.getAllpairDistance(ins->dummy_goals[pusher]->index, v_puller->index) : D.get(pusher, v_puller);
522:     int pusher_vpusher = instance.getAllpairDistance(pusher_goal,v_pusher->index);
523:     //A[pusher]->reached_goal ? instance.getAllpairDistance(ins->dummy_goals[pusher]->index, v_pusher->index) : D.get(pusher, v_pusher);
524:     int puller_vpuller = instance.getAllpairDistance(puller_goal,v_puller->index);
525:     //A[puller]->reached_goal ? instance.getAllpairDistance(ins->dummy_goals[puller]->index, v_puller->index) : D.get(puller, v_puller);
526:     int puller_vpusher = instance.getAllpairDistance(puller_goal,v_pusher->index);
527:     //A[puller]->reached_goal ? instance.getAllpairDistance(ins->dummy_goals[puller]->index, v_pusher->index) : D.get(puller, v_pusher);
528: 
529: 
530:     Vertex* tmp = nullptr;
531:     //while (D.get(pusher, v_puller) < D.get(pusher, v_pusher)) {
532:       //while ((!A[pusher]->reached_goal && A[puller]->reached_goal) || (!A[pusher]->reached_goal && !A[puller]->reached_goal && pusher_vpuller < pusher_vpusher)) {
533:     while ((pusher_vpuller < pusher_vpusher)) 
534:     {
535:         auto n = v_puller->neighbor.size();
536:         // remove agents who need not to move
537:         for (auto u : v_puller->neighbor) 
538:         {
539:             auto a = occupied_now[u->id];
540:             if (u == v_pusher ||
541:                 (u->neighbor.size() == 1 && a != nullptr && ins->goals[a->id] == u)) 
542:             {
543:                 --n;
544:             } 
545:             else 
546:             {
547:                 tmp = u;
548:             }
549:         }
550: 
551:         if (n >= 2) return false;  // able to swap
552:         if (n <= 0) break;
553: 
554:         v_pusher = v_puller;
555:         v_puller = tmp;
556: 
557:         // int pusher_vpuller = instance.getAllpairDistance(pusher_goal,v_puller->index);
558:         // int pusher_vpusher = instance.getAllpairDistance(pusher_goal,v_pusher->index);
559:         // int puller_vpuller = instance.getAllpairDistance(puller_goal,v_puller->index);
560:         // int puller_vpusher = instance.getAllpairDistance(puller_goal,v_pusher->index);
561:         int pusher_vpuller = instance.getAllpairDistance(pusher_goal,v_puller->index);
562:         int pusher_vpusher = instance.getAllpairDistance(pusher_goal,v_pusher->index);
563:         int puller_vpuller = instance.getAllpairDistance(puller_goal,v_puller->index);
564:         int puller_vpusher = instance.getAllpairDistance(puller_goal,v_pusher->index);
565:     }
566: 
567:     return (puller_vpusher < puller_vpuller) &&
568:             (pusher_vpusher == 0 || pusher_vpuller < pusher_vpusher);
569: }

额外已亲核源接口：
- LACAMInstance的SharedEnv构造只按curr_states建立starts、按goal_locations每行front建立goals；N为env->num_of_agents，没有追加第二goal。
- runLACAM2用该ins、原局部MT/Deadline/参数调用solve；返回空则false，非空才复制路径/按首目标到达时刻取原段；不以真实TASK更新env。
- 一次HNode构造存的reach_goal之后不因rewrite的parent更新而改写；range归纳与parent指针/深度语义是两回事。
- prepareDummy没有改env->goal_locations，不能拿dummy数量当队列覆盖证明。
- 原后处理/外层全proposal验证及唯一合法物理授权仍保留，任何新增source修订对所有内部引用臂共同应用，实际分支、比较、输入读取、失败与内存工作全费。
