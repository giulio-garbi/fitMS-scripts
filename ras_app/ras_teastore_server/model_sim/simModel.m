%Cli persistence webui
RT0 = [1.1816136324603659 0.06429236520332181 0.17107037960859117];
ST0 = [0 0 0 0 0];
ST0(1) = RT0(1)-RT0(3);
ST0(2) = RT0(2);
ST0(3) = RT0(3)-RT0(2);

X0 = zeros([1 13]);

for i=1:size(Cli,1)
    c = Cli(i);
    disp(c);
    X0(end)=c;
    % persistence, auth, image, webui, Client
    MU([5,8,11,12,13])=[1/ST0(2),0,0,1/ST0(3),1/ST0(1)];
    NT=[inf,inf,inf,inf,inf];
    TF=30;
    rep=5000;
    X = lqn([X0 zeros([1,5])],MU,NT,NC,TF,rep,3);
    lastQl = mean(X(:,end,:),3)';
    Thr = lastQl(14:end)/TF;
    STs = lastQl([5,8,11,12,13])./Thr;
    STs(isnan(STs)) = 0;

    % Client, persistence, webui
    if i==1
        RTs = [STs(1) + STs(4) + STs(5), STs(1), STs(1) + STs(4)];
        Ths = [Thr(end)];
    else
        RTs = [RTs;STs(1) + STs(4) + STs(5), STs(1), STs(1) + STs(4)];
        Ths = [Ths;Thr(end)];
    end
end