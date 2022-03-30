function X = lqn(X0,MU,NT,NC,TF,rep,dt)
import Gillespie.*

% Make sure vector components are doubles
X0 = double(X0);
MU = double(MU);

% Make sure all vectors are row vectors
if(iscolumn(X0))
    X0 = X0';
end
if(iscolumn(MU))
    MU = MU';
end
if(iscolumn(NT))
    NT = NT';
end
if(iscolumn(NT))
    NC = NC';
end

p.MU = MU; 
p.NT = NT;
p.NC = NC;
p.delta = 10^5; % context switch rate (super fast)

%states name
%X(1)=XBrowse_Client2Home;
%X(2)=XHome_a;
%X(3)=XHome_Home2Cat;
%X(4)=XCat_a;
%X(5)=XCat_e;
%X(6)=XHome_Home2IsLogged;
%X(7)=XIsLogged_a;
%X(8)=XIsLogged_e;
%X(9)=XHome_Home2GetImg;
%X(10)=XGetImg_a;
%X(11)=XGetImg_e;
%X(12)=XHome_e;
%X(13)=XBrowse_browse;

%X(14)=Compl_Cat
%X(15)=Compl_IsLogged
%X(16)=Compl_GetImg
%X(17)=Compl_Home
%X(18)=Compl_Browse


%task ordering
%1=Client;
%2=WebUI;
%3=Persistence;
%4=Auth;
%5=Image;


% Jump matrix
stoich_matrix=[+1,  +1,  +0,  +0,  +0,  +0,  +0,  +0,  +0,  +0,  +0,  +0,  -1, 0,0,0,0,1;
               +0,  -1,  +1,  +1,  +0,  +0,  +0,  +0,  +0,  +0,  +0,  +0,  +0, 0,0,0,0,0;
               +0,  +0,  +0,  -1,  +1,  +0,  +0,  +0,  +0,  +0,  +0,  +0,  +0, 0,0,0,0,0;
               %+0,  +0,  -1,  +0,  -1, +1,  +1,  +0,  +0,  +0,  +0,  +0,  +0, 1,0,0,0,0;
               +0,  +0,  -1,  +0,  -1,  +0,  +0,  +0,  +0,  +0,  +0,  +1,  +0, 1,0,0,0,0;
               +0,  +0,  +0,  +0,  +0,  +0,  -1,  +1,  +0,  +0,  +0,  +0,  +0, 0,0,0,0,0;
               +0,  +0,  +0,  +0,  +0,  -1,  +0,  -1,  +1,  +1,  +0,  +0,  +0, 0,1,0,0,0;
               +0,  +0,  +0,  +0,  +0,  +0,  +0,  +0,  +0,  -1,  +1,  +0,  +0, 0,0,0,0,0;
               +0,  +0,  +0,  +0,  +0,  +0,  +0,  +0,  -1,  +0,  -1,  +1,  +0, 0,0,1,0,0;
               -1,  +0,  +0,  +0,  +0,  +0,  +0,  +0,  +0,  +0,  +0,  -1,  +1, 0,0,0,1,0;
               ];
    
tspan = [0, TF];
pfun = @propensities_2state;
 
X = zeros(length(X0), ceil(TF/dt) + 1, rep);
for i = 1:rep
    [t, x] = directMethod(stoich_matrix, pfun, tspan, X0, p);
    tsin = timeseries(x,t);
    tsout = resample(tsin, linspace(0, TF, ceil(TF/dt)+1), 'zoh');
    X(:, :, i) = tsout.Data';
end

end

% Propensity rate vector (CTMC)
function Rate = propensities_2state(X, p)
    Rate = [p.MU(13)*X(13);
    		X(2)/(X(2))*p.delta*min(X(2),p.NT(2)-(X(3)+X(6)+X(9)+X(12)));
    		X(4)/(X(4))*p.delta*min(X(4),p.NT(3)-(X(5)));
    		X(3)/(X(3))*X(5)/(X(5)+X(8)+X(11)+X(12))*min(X(5)+X(8)+X(11)+X(12),p.NC(2))*p.MU(5);
    		X(7)/(X(7))*p.delta*min(X(7),p.NT(4)-(X(8)));
    		X(6)/(X(6))*X(8)/(X(5)+X(8)+X(11)+X(12))*min(X(5)+X(8)+X(11)+X(12),p.NC(2))*p.MU(8);
    		X(10)/(X(10))*p.delta*min(X(10),p.NT(5)-(X(11)));
    		X(9)/(X(9))*X(11)/(X(5)+X(8)+X(11)+X(12))*min(X(5)+X(8)+X(11)+X(12),p.NC(2))*p.MU(11);
    		X(1)/(X(1))*X(12)/(X(5)+X(8)+X(11)+X(12))*min(X(5)+X(8)+X(11)+X(12),p.NC(2))*p.MU(12);
    		];
    Rate(isnan(Rate))=0;
end