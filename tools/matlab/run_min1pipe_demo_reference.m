function run_min1pipe_demo_reference(out_dir, force_overwrite)
%RUN_MIN1PIPE_DEMO_REFERENCE Generate deterministic MATLAB reference outputs.
%
% Usage (from MATLAB):
%   run_min1pipe_demo_reference();
%   run_min1pipe_demo_reference('/abs/output/path', true);

    if nargin < 1 || isempty(out_dir)
        ts = char(datetime('now', 'TimeZone', 'UTC', 'Format', 'yyyyMMdd''T''HHmmss''Z'''));
        out_dir = fullfile(repo_root(), 'artifacts', 'golden', 'matlab', 'demo_data', ts);
    end
    if nargin < 2 || isempty(force_overwrite)
        force_overwrite = false;
    end

    out_dir = char(out_dir);
    fprintf('[%s] MATLAB reference output dir: %s\n', stamp(), out_dir);

    if isfolder(out_dir) && force_overwrite
        rmdir(out_dir, 's');
    end
    if ~isfolder(out_dir)
        mkdir(out_dir);
    end

    work_dir = fullfile(out_dir, 'work');
    if isfolder(work_dir)
        rmdir(work_dir, 's');
    end
    mkdir(work_dir);

    root = repo_root();
    addpath(genpath(root));
    ensure_cvx_on_path(root);

    src_demo = fullfile(root, 'demo', 'demo_data.tif');
    if ~isfile(src_demo)
        error('Demo dataset not found: %s', src_demo);
    end
    dst_demo = fullfile(work_dir, 'demo_data.tif');
    copyfile(src_demo, dst_demo);

    fprintf('[%s] Running min1pipe_HPC on scratch dataset...\n', stamp());
    [fname, frawname, fregname] = min1pipe_HPC(20, 20, [], [], true, 1, [work_dir, filesep], 'demo_data.tif');
    fprintf('[%s] Processing complete: %s\n', stamp(), fname);

    load(fname);
    fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100, 100, 1278, 907]);
    clf;

    subplot(2, 3, 1, 'align');
    imagesc(imaxn);
    axis square;
    title('Raw');

    subplot(2, 3, 2, 'align');
    imagesc(imaxy);
    axis square;
    title('Before MC');

    subplot(2, 3, 3, 'align');
    imagesc(imax);
    axis square;
    title('After MC');

    subplot(2, 3, 4, 'align');
    plot_contour(roifn, sigfn, seedsfn, imax, pixh, pixw);
    axis square;

    subplot(2, 3, 5, 'align');
    axis off;
    plot(raw_score);
    hold on;
    plot(corr_score);
    hold off;
    axis square;
    title('MC Scores');

    subplot(2, 3, 6, 'align');
    sigt = sigfn;
    for i = 1:size(sigt, 1)
        sigt(i, :) = normalize(sigt(i, :));
    end
    plot((sigt + (1:size(sigt, 1))')');
    axis tight;
    axis square;
    title('Traces');

    fig_path = fullfile(out_dir, 'demo_visualization_matlab.png');
    exportgraphics(fig, fig_path, 'Resolution', 150);
    close(fig);

    copyfile(fname, fullfile(out_dir, 'demo_data_data_processed.mat'));
    copyfile(frawname, fullfile(out_dir, 'demo_data_frame_all.mat'));
    copyfile(fregname, fullfile(out_dir, 'demo_data_reg.mat'));

    manifest = struct();
    manifest.generated_utc = char(datetime('now', 'TimeZone', 'UTC', 'Format', 'yyyy-MM-dd''T''HH:mm:ss''Z'''));
    manifest.repo_root = root;
    manifest.matlab_version = version;
    manifest.input_dataset = src_demo;
    manifest.parameters = struct('Fsi', 20, 'Fsi_new', 20, 'ismc', true, 'flag', 1);
    manifest.outputs = struct( ...
        'processed', fullfile(out_dir, 'demo_data_data_processed.mat'), ...
        'raw', fullfile(out_dir, 'demo_data_frame_all.mat'), ...
        'reg', fullfile(out_dir, 'demo_data_reg.mat'), ...
        'figure', fig_path ...
    );

    manifest_path = fullfile(out_dir, 'reference_manifest.json');
    fid = fopen(manifest_path, 'w');
    if fid < 0
        error('Unable to write manifest: %s', manifest_path);
    end
    fwrite(fid, jsonencode(manifest), 'char');
    fclose(fid);

    fprintf('[%s] Wrote MATLAB reference artifacts:\n', stamp());
    fprintf('  - %s\n', fullfile(out_dir, 'demo_data_data_processed.mat'));
    fprintf('  - %s\n', fullfile(out_dir, 'demo_data_frame_all.mat'));
    fprintf('  - %s\n', fullfile(out_dir, 'demo_data_reg.mat'));
    fprintf('  - %s\n', fig_path);
    fprintf('  - %s\n', manifest_path);
end

function out = repo_root()
    here = fileparts(mfilename('fullpath'));
    out = fileparts(fileparts(here));
end

function out = stamp()
    out = char(datetime('now', 'TimeZone', 'UTC', 'Format', 'yyyy-MM-dd HH:mm:ss'));
end

function ensure_cvx_on_path(root)
    cvx_root = getenv('MIN1PIPE_CVX_ROOT');
    if isempty(cvx_root)
        cvx_root = fullfile(root, 'artifacts', 'third_party', 'cvx');
    end
    cvx_begin = fullfile(cvx_root, 'commands', 'cvx_begin.m');
    if ~isfile(cvx_begin)
        warning('CVX root does not contain cvx_begin.m: %s', cvx_root);
        return;
    end

    fprintf('[%s] Adding CVX path: %s\n', stamp(), cvx_root);
    warning('off', 'MATLAB:dispatcher:nameConflict');
    addpath(genpath(cvx_root));
    warning('on', 'MATLAB:dispatcher:nameConflict');

    cvx_setup_script = fullfile(cvx_root, 'cvx_setup.m');
    if isfile(cvx_setup_script)
        try
            evalc('run(cvx_setup_script)');
        catch ME
            warning('CVX setup warning: %s', ME.message);
        end
    end

    try
        pool = gcp('nocreate');
        if isempty(pool)
            pool = parpool('Processes');
        end
        cvx_root_esc = strrep(cvx_root, '''', '''''');
        pctRunOnAll(sprintf([ ...
            'warning(''off'',''MATLAB:dispatcher:nameConflict'');', ...
            'addpath(genpath(''%s''));', ...
            'warning(''on'',''MATLAB:dispatcher:nameConflict'');'], cvx_root_esc));
    catch ME
        warning('Unable to prepare CVX on workers: %s', ME.message);
    end
end
