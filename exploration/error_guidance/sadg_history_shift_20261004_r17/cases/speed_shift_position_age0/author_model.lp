\Problem name: SADG_RHC

Minimize
OBJROW: v_0_6_g + v_1_6_g
Subject To
v_0_0_s_to_v_0_0_g:  - v_0_0_s + v_0_0_g >= 1.01000
v_0_1_s_to_v_0_1_g:  - v_0_1_s + v_0_1_g >= 1.01000
v_0_2_s_to_v_0_2_g:  - v_0_2_s + v_0_2_g >= 1.01000
v_0_3_s_to_v_0_3_g:  - v_0_3_s + v_0_3_g >= 1.01000
v_0_4_s_to_v_0_4_g:  - v_0_4_s + v_0_4_g >= 1.01000
v_0_5_s_to_v_0_5_g:  - v_0_5_s + v_0_5_g >= 1.01000
v_0_6_s_to_v_0_6_g:  - v_0_6_s + v_0_6_g >= 1.01000
v_1_0_s_to_v_1_0_g:  - v_1_0_s + v_1_0_g >= 1.01000
v_1_1_s_to_v_1_1_g:  - v_1_1_s + v_1_1_g >= 1.01000
v_1_2_s_to_v_1_2_g:  - v_1_2_s + v_1_2_g >= 1.01000
v_1_3_s_to_v_1_3_g:  - v_1_3_s + v_1_3_g >= 1.01000
v_1_4_s_to_v_1_4_g:  - v_1_4_s + v_1_4_g >= 1.01000
v_1_5_s_to_v_1_5_g:  - v_1_5_s + v_1_5_g >= 1.01000
v_1_6_s_to_v_1_6_g:  - v_1_6_s + v_1_6_g >= 1.01000
v_0_0_g_to_v_0_1_s:  - v_0_0_g + v_0_1_s >= 0.01000
v_0_1_g_to_v_0_2_s:  - v_0_1_g + v_0_2_s >= 0.01000
v_0_2_g_to_v_0_3_s:  - v_0_2_g + v_0_3_s >= 0.01000
v_0_3_g_to_v_0_4_s:  - v_0_3_g + v_0_4_s >= 0.01000
v_0_4_g_to_v_0_5_s:  - v_0_4_g + v_0_5_s >= 0.01000
v_0_5_g_to_v_0_6_s:  - v_0_5_g + v_0_6_s >= 0.01000
v_1_0_g_to_v_1_1_s:  - v_1_0_g + v_1_1_s >= 0.01000
v_1_1_g_to_v_1_2_s:  - v_1_1_g + v_1_2_s >= 0.01000
v_1_2_g_to_v_1_3_s:  - v_1_2_g + v_1_3_s >= 0.01000
v_1_3_g_to_v_1_4_s:  - v_1_3_g + v_1_4_s >= 0.01000
v_1_4_g_to_v_1_5_s:  - v_1_4_g + v_1_5_s >= 0.01000
v_1_5_g_to_v_1_6_s:  - v_1_5_g + v_1_6_s >= 0.01000
sw_fwd_v_0_4_g_to_v_1_3_s:  - v_0_4_g + v_1_3_s + 1000000 dg_agent0_0 >= 0.01000
sw_rev_v_1_4_g_to_v_0_3_s:  v_0_3_s - v_1_4_g -1000000 dg_agent0_0 >= -999999.99000
boundary_v_0_1_g:  v_0_1_g >= 0.62500
boundary_v_1_1_g:  v_1_1_g >= 0.50000
Bounds
 v_0_0_s Free
 v_0_0_g Free
 v_0_1_s Free
 v_0_1_g Free
 v_0_2_s Free
 v_0_2_g Free
 v_0_3_s Free
 v_0_3_g Free
 v_0_4_s Free
 v_0_4_g Free
 v_0_5_s Free
 v_0_5_g Free
 v_0_6_s Free
 v_0_6_g Free
 v_1_0_s Free
 v_1_0_g Free
 v_1_1_s Free
 v_1_1_g Free
 v_1_2_s Free
 v_1_2_g Free
 v_1_3_s Free
 v_1_3_g Free
 v_1_4_s Free
 v_1_4_g Free
 v_1_5_s Free
 v_1_5_g Free
 v_1_6_s Free
 v_1_6_g Free
 0 <= dg_agent0_0 <= 1
Integers
dg_agent0_0 
End
