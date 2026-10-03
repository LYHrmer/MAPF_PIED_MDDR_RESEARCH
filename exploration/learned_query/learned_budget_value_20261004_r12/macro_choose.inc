    std::string choose(const std::vector<Candidate>& input,const R& at,unsigned capacity,const std::string& policy,unsigned opportunity,const std::string& trigger)const{
        const std::vector<std::string> options={"C","W","E","L","ED","LD"};
        std::vector<Candidate> visible=input;
        for(auto& c:visible){
            const R budget=rat(capacity,16),time=O::div(floor6(O::div(at,rat(8))),rat(16));
            c.features.push_back(budget);c.features.push_back(time);
            c.features.push_back(O::mul(budget,c.features.at(19)));c.features.push_back(O::mul(budget,O::sub(rat(1),time)));
            check(c.features.size()==24,"R12 candidate feature dimensions");
        }
        if(macro_name.empty()){
            check(capacity==8||capacity==16,"R12 initial public budget");initial_capacity=capacity;
            std::vector<R> gate(25,rat(0));
            for(const auto& c:visible)for(unsigned j=0;j<24;++j)gate[j]=O::add(gate[j],O::div(c.features[j],rat(visible.size())));
            gate[24]=rat(visible.size(),16);
            std::vector<R> task_scores(6,rat(0)),time_scores(6,rat(0)),scores(6,rat(0));
            R margin=rat(0);bool infinite=false,learned=false;unsigned selected_option=0;
            const auto inference_start=std::chrono::steady_clock::now();
            if(policy=="WAIT")selected_option=1;
            else if(policy.substr(0,6)=="macro_"){
                const auto it=std::find(options.begin(),options.end(),policy.substr(6));check(it!=options.end(),"fixed macro support");selected_option=static_cast<unsigned>(it-options.begin());
            } else if(policy=="budget_lookup"){
                const auto& value=parameters.at("budget_lookup_"+std::to_string(capacity));check(value.size()==1,"budget lookup binding");bool found=false;
                for(unsigned k=0;k<6;++k)if(same(value[0],rat(k))){selected_option=k;found=true;}
                check(found,"budget lookup option range");
            } else if(policy!="condition"){
                check(policy=="full"||policy=="nohistory"||policy=="nobudget"||policy=="tasks_only","learned selector variant");learned=true;
                const auto& threshold=parameters.at("shared_margin");check(threshold.size()==2,"shared CAL threshold binding");infinite=same(threshold[0],rat(1));margin=threshold[1];
                const std::string variant=policy=="tasks_only"?"full":policy;
                for(unsigned k=1;k<6;++k){
                    for(unsigned head=0;head<2;++head){
                        if(head==1&&policy=="tasks_only")continue;
                        const auto& coefficient=parameters.at(variant+"_"+options[k]+(head==0?"_tasks":"_time"));check(coefficient.size()==26,"R12 ridge coefficient dimensions");R value=coefficient[0];
                        for(unsigned j=0;j<25;++j){
                            const bool masked=(policy=="nohistory"&&j>=10&&j<18)||(policy=="nobudget"&&(j==20||j==22||j==23));
                            if(!masked)value=O::add(value,O::mul(coefficient[j+1],gate[j]));
                        }
                        if(head==0)task_scores[k]=value;else time_scores[k]=value;
                    }
                    scores[k]=O::add(task_scores[k],time_scores[k]);
                    if(!infinite&&O::cmp(scores[k],margin)>0&&(selected_option==0||O::cmp(scores[k],scores[selected_option])>0))selected_option=k;
                }
            }
            macro_name=options[selected_option];
            const auto inference_ns=learned?std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now()-inference_start).count():0;
            std::cout<<"{\"event\":\"macro_choice\",\"at\":";bound3(at);
            std::cout<<",\"policy\":\""<<policy<<"\",\"opportunity\":"<<opportunity<<",\"initial_capacity\":"<<initial_capacity<<",\"features\":[";
            bool comma=false;for(const auto& x:gate){if(comma)std::cout<<',';
            comma=true;std::cout<<'"'<<exact(x)<<'"';}
            std::cout<<"],\"learned\":"<<(learned?"true":"false")<<",\"margin_infinite\":"<<(infinite?"true":"false")<<",\"margin\":\""<<exact(margin)<<"\",\"scores\":[";
            for(unsigned k=0;k<6;++k){if(k)std::cout<<',';std::cout<<"{\"option\":\""<<options[k]<<"\",\"tasks\":\""<<exact(task_scores[k])<<"\",\"time\":\""<<exact(time_scores[k])<<"\",\"total\":\""<<exact(scores[k])<<"\"}";}
            std::cout<<"],\"selected_option\":\""<<macro_name<<"\",\"inference_calls\":"<<(learned?1:0)<<",\"inference_ns\":"<<inference_ns<<"}\n";
        }
        std::string scoring_policy=macro_name=="W"?"WAIT":"condition";unsigned intervention_index=0;std::vector<std::string> second_eligible;
        const bool early=macro_name=="E"||macro_name=="ED",late=macro_name=="L"||macro_name=="LD",twice=macro_name=="ED"||macro_name=="LD";
        const bool first=(early||late)&&pair_stage==0&&capacity>0&&(early||initial_capacity-capacity>=initial_capacity/2);
        const bool second=twice&&pair_stage==1&&capacity>0;
        if(first||second){
            const Candidate* target=nullptr;R best=rat(0);
            for(const auto& c:visible){
                if(second&&c.agent==anchor_agent&&c.key==anchor_move)continue;
                if(second)second_eligible.push_back(c.key);
                R score=rat(0);const R probability=survival_release_probability(c.agent,O::sub(at,c.launch));
                for(const auto& claim:c.claims)score=O::add(score,O::div(probability,rat(claim.remaining*claim.owners)));
                if(!target||O::cmp(score,best)>0||(same(score,best)&&(c.agent<target->agent||(c.agent==target->agent&&c.key<target->key)))){target=&c;best=score;}
            }
            if(target){
                scoring_policy="force_SKIP"+std::to_string(target->agent);intervention_index=first?1:2;pair_stage=intervention_index;
                if(first){anchor_agent=target->agent;anchor_move=target->key;for(const auto& c:target->claims)anchor_tasks.insert(c.task);}
            }
        }
        std::string selected,selected_kind="WAIT";R best=rat(0);unsigned best_agent=1000,best_kind=2;
        std::cout<<"{\"event\":\"actor_decision\",\"at\":";bound3(at);
        std::cout<<",\"policy\":\""<<policy<<"\",\"remaining_capacity\":"<<capacity<<",\"decision_mode\":\""<<scoring_policy<<"\",\"opportunity\":"<<opportunity<<",\"trigger\":\""<<trigger<<"\",\"RR_cursor\":"<<rr_cursor<<",\"candidates\":[";
        bool comma=false;
        for(const auto& c:visible){
            check(O::cmp(O::sub(at,c.launch),rat(3,4))>=0,"R12 original age gate");check(has_history(c.agent)&&known>=2,"R12 original public history gate");
            const R p=survival_release_probability(c.agent,O::sub(at,c.launch));std::vector<R> scores={rat(0),rat(0)};
            for(unsigned kind=0;kind<2;++kind){
                R score=rat(0);const std::string name=kind==0?"QUERY":"SKIP";
                if(scoring_policy.substr(0,6)=="force_")score=scoring_policy.substr(6)==name+std::to_string(c.agent)?rat(1):rat(0);
                else if(scoring_policy=="condition"&&kind==0)for(const auto& cl:c.claims)score=O::add(score,O::div(p,rat(cl.remaining*cl.owners)));
                scores[kind]=score;const bool tie=kind<best_kind||(kind==best_kind&&(c.agent<best_agent||(c.agent==best_agent&&c.key<selected)));
                if(capacity&&O::cmp(score,rat(0))>0&&(selected.empty()||O::cmp(score,best)>0||(same(score,best)&&tie))){selected=c.key;selected_kind=name;best=score;best_agent=c.agent;best_kind=kind;}
            }
            if(comma)std::cout<<',';
            comma=true;
            std::cout<<"{\"move\":\""<<c.key<<"\",\"agent\":"<<c.agent<<",\"heading\":\""<<c.heading<<"\",\"public_launch\":";bound3(c.launch);
            std::cout<<",\"probability\":\""<<exact(p)<<"\",\"score\":\""<<exact(scores[0])<<"\",\"skip_score\":\""<<exact(scores[1])<<"\",\"claims\":[";
            bool cc=false;for(const auto& cl:c.claims){if(cc)std::cout<<',';cc=true;std::cout<<"{\"task\":"<<cl.task<<",\"remaining_route_items\":"<<cl.remaining<<",\"owners\":"<<cl.owners<<'}';}
            std::cout<<"],\"features\":[";bool ff=false;for(const auto& z:c.features){if(ff)std::cout<<',';ff=true;std::cout<<'"'<<exact(z)<<'"';}std::cout<<"]}";
        }
        std::cout<<"],\"macro\":\""<<macro_name<<"\",\"initial_capacity\":"<<initial_capacity<<",\"intervention_index\":"<<intervention_index<<",\"pair_stage\":"<<pair_stage<<",\"anchor_agent\":"<<anchor_agent<<",\"anchor_move\":\""<<anchor_move<<"\",\"anchor_tasks\":[";
        bool ac=false;for(unsigned task:anchor_tasks){if(ac)std::cout<<',';ac=true;std::cout<<task;}
        std::cout<<"],\"second_eligible\":[";ac=false;for(const auto& key:second_eligible){if(ac)std::cout<<',';ac=true;std::cout<<'"'<<key<<'"';}
        std::cout<<"],\"head_lineage_count\":"<<public_head_parent.size()<<",\"selected\":\""<<selected<<"\",\"selected_kind\":\""<<selected_kind<<"\",\"END_only_known\":"<<known<<",\"END_unknown\":"<<unknown<<",\"private_progress_input\":false,\"regime_input\":false,\"future_head_input\":false}\n";
        return selected_kind=="SKIP"?"SKIP:"+selected:selected;
    }
