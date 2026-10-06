# tree_dynamics (old notebook: Farm Dynamics.ipynb, cells 7-8)
| New figure | Shows | Replaces |
|---|---|---|
| `tree_behaviour_by_district_li_group.png` (+csv) | 100% bars of: has planted trees / remnant only x removed trees yes/no, by district and LI group; chi-square for removal | `tree_behavior`, left panel of `combined_tree_dynamics` |
| `trees_planted_removed_counts.png` (+csv) | Number of trees planted, number removed (removers only) and net change, by district (points + median) | `net_tree_change`, right panel of `combined_tree_dynamics` |

What changed and why (main error in the old version)
- The planting question ('Have you planted or removed trees' / 'Planted') is skip-logic. It was asked only of the 78 HH who ticked 'planted' as a separate tree-origin option, not of the 407 who answered 'both'. The old code read every unanswered case as 'No' and as 0 planted. So most HH became 'Neither' or 'Removal only', and net change was mostly -removed.
- Fix: 'has planted trees' now comes from tree origin (planted or both; all 597 answered). Removal comes from Q120 (594 valid). The planted counts and net change are shown only for the sub-sample asked (n = 77 with a count) and are labelled as a sub-sample.
- Removal is far more common in Mukono (63% vs 35%; p < 0.001). It does not differ by LI group (p = 0.44).
- Outliers are kept and flagged rather than trimmed at the 95th percentile. One Nakaseke HH reports 15,000 trees planted and one reports 1,000 removed; neither is verified.
- Combined figure dropped: its two panels are the two figures above.
