
"""
Class to parse input commands as strings and call apropriate parent agent's methods
"""

class AgentStringCommandParser():
    def __init__(self, agent):
        self.agent = agent

    def processStringCommand(self, data):
        print("Agent #{:d} - processing string command:{:s}".format(self.agent.agentN, data.decode()))

        if data.find(b'@BS') != -1:
            #print ("self.agent.BsAnswerReceived = True")
            self.agent.BsAnswerReceived = True

        """
        if data.find(b'@TL') != -1:
            self.sendPacketWithNumberingToServer('@TL:{:03d}'.format(self.currentTxPacketN).encode('utf-8'))



        if data.find(b'@TS') != -1:
            self.sendPacketWithNumberingToServer(b'@TS:24,29,29,29,29,25,25,25,25')

        if data.find(b'@OP') != -1:
            self.sendPacketWithNumberingToServer(b'@OP:10000')
        """

"""
serverHandleMsg
  :: Known urg
  => ServerEnv meta -> ServerAgentSkel meta -> Msg 'Client urg -> IO ()
serverHandleMsg serverEnv agent =
  let ServerEnv started logging moveEnv talkEnv _ notifs = serverEnv
      routeConst   = _moveRouteConst moveEnv
      TalkEnv powerSupply managerInterface = talkEnv
  in join $ \(Msg _ _ _ (Same stamp) _) -> genericHandleMsg logging agent $ \case
    Unk str        -> logInf logging agent str
    Inf _          -> return ()
    War war        -> do
      logInf logging agent . netSerial $ War war
      getContentsNotif routeConst agent war >>= uncurry (reportNotif notifs)
    Err err        -> do
      clearAgent logging agent err
      reportAST agent managerInterface $ ERR err
    HW  _          -> fail "serverHandleMsg: a HW can't be here"
    BS (Same batt) -> do
      agent & _AnsAgentBatt .~ batt
      agent & _SetAgentTour . _TourVolt .~ _supercap batt
      reportAST agent managerInterface . SUP $ _supercap batt
    TS (Same temp) -> agent & _AnsAgentTemp .~ temp
    TL (Same left) -> agent & _AnsAgentLeft .~ left
    OP (Same odos) -> case odos of
      Uncertain     -> endAgentOdom agent
      Certain odom' ->
        void $ updateOdom logging (Stamped stamp odom') agent
    BR (Same brst) -> do
      agent & _SetAgentBrSt .~ brst
      task <- getAgentTask agent
      when (task == TaskErr && brst == FreeWheel) $
        agent & _SetAgentTask .~ TaskID
    SC  sc         -> case sc of {}
    OZ             -> resetAgentOdom agent
    OD  odom'      -> do
      updateOdom logging (Stamped stamp odom') agent
      logAgentDist logging agent
      interval started >>= logAgentTime logging agent
    DE             -> cutAgentRoad logging StepDE agent
    CB             -> do
      getAgentTour agent >>= traverse interval
                         >>= logDeb logging agent . Text.unpack . pShowNoColor
      newAgentTour >>= \tour -> agent & _SetAgentTour .~ tour
      chargeBegin powerSupply
    CE             -> chargeEnd powerSupply
    NT task'       -> do
      AgentBusy task from <- getAgentBusy agent
      int <- interval from
      logAll logging agent $ printf "### task finished in %.1fs" int
      if task == TaskErr
        then logInf logging agent $
          "&&& an agent in error state returned a new task: " ++ netSerial task'
        else agent & _SetAgentTask .~ task'
      when (task' == TaskID) $ reportAST agent managerInterface IDL
"""