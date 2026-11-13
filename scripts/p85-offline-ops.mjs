/** Explicit offline-only snapshot CLI; no scheduled jobs, no remote I/O. */
import {createOfflineSnapshot,restoreOfflineSnapshot} from '../enterprise/p85-offline-backup.mjs';

const args=process.argv.slice(2);
const usage='Usage: node scripts/p85-offline-ops.mjs <snapshot|restore> --source <absolute-directory> --dest <new-absolute-directory> (STOP vault before use)';
if(args.length!==5||!['snapshot','restore'].includes(args[0])||
  args[1]!=='--source'||args[3]!=='--dest'||
  typeof args[2]!=='string'||typeof args[4]!=='string'){
  process.stderr.write(usage+'\n');process.exitCode=2;
}else{
  try{
    const result=args[0]==='snapshot'?await createOfflineSnapshot({root:args[2],destination:args[4]}):
      restoreOfflineSnapshot({snapshot:args[2],destination:args[4]});
    process.stdout.write(JSON.stringify(result)+'\n');
  }catch(e){process.stderr.write(JSON.stringify({error:e?.code||'OFFLINE_OPERATION_FAILED'})+'\n');process.exitCode=1;}
}
