<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.1/graphml.xsd">
  <key id="name" for="node" attr.name="name" attr.type="string" />
  <key id="lim_inf" for="node" attr.name="lim_inf" attr.type="float" />
  <key id="lim_sup" for="node" attr.name="lim_sup" attr.type="float" />
  <key id="x0" for="node" attr.name="x0" attr.type="float" />
  <key id="w" for="node" attr.name="w" attr.type="float" />
  <graph id="G" edgedefault="undirected">
    <node id="0">
        <data key="name">Alex</data>
        <data key="lim_inf">0.4</data>
        <data key="lim_sup">1.2</data>
        <data key="x0">0.8</data>
        <data key="w">0.1</data>
    </node>
    <node id="1">
        <data key="name">Bob</data>
        <data key="lim_inf">0.2</data>
        <data key="lim_sup">1.0</data>
        <data key="x0">0.6</data>
        <data key="w">0.1</data>
    </node>
    <node id="2">
        <data key="name">Carol</data>
        <data key="lim_inf">0.0</data>
        <data key="lim_sup">0.8</data>
        <data key="x0">0.4</data>
        <data key="w">0.1</data>
    </node>
    <node id="3">
        <data key="name">Dave</data>
        <data key="lim_inf">-0.2</data>
        <data key="lim_sup">0.4</data>
        <data key="x0">0.2</data>
        <data key="w">0.1</data>
    </node>
    <edge id="4" source="0" target="1" label="knows"></edge>
    <edge id="5" source="0" target="2" label="knows"></edge>
    <edge id="6" source="0" target="3" label="knows"></edge>
    <edge id="7" source="2" target="3" label="knows"></edge>
  </graph>
</graphml>